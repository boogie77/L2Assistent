﻿# Библиотеки для управления виртуальной клавиатурой и мышью
from AutoHotPy import AutoHotPy
# Библиотека для захвата и анализа экрана
from libs.screen import ScreenTools
# Библиотека для удаленного управления персонажами в команде
from libs.team_server import TeamServer
# Системные библиотеки
import os
import threading
import time
import numpy as np
import cv2
from datetime import datetime


class Character(object):
    """Класс описывает свойства и методы управления персонажем"""

    def __init__(self, debug_mode=False, attack_mode=False):
        # Константы
        self.useKeyboard = True  # Использование клавиатуры вместо мыши для нажатия на макросы
        self.debugMode = debug_mode  # Режим отладки
        self.attackMode = attack_mode  # Режим боя
        self.isRunning = False  # Признак запуска бота
        # Дополнительные объекты
        self.virtualKeyboard = AutoHotPy()  # Виртуальная клавиатура
        self.virtualKeyboard.registerExit(self.virtualKeyboard.ESC, self.stopAutoHotPy)
        self.screen = ScreenTools()  # Средство анализа экрана
        self.server = None  # Средство для удаленного управления персонажами
        self.blockKeyboard = False  # Блокирование клавиатуры
        # Характеристики персонажа
        self.HP = None
        self.MP = None
        self.CP = None
        self.isDead = False
        # Характеристики цели
        self.hasTarget = None  # Признак наличия цели
        self.targetHP = None  # Количество пикселей со здоровьем Цели
        self.targetNoHP = None  # Количество пикселей с отсутствующим здоровьем цели
        self.startAttackTime = None  # Время начала атаки
        self.everyTenSecondsTargetHP = None  # Количество здоровья цели 10 секунд назад
        self.everyTenSecondsTry = 0  # Количество попыток атаки цели (1 попытка = более 10 секунд цель не атакована)
        self.currentTenSeconds = 0  # Текущая десятка секунд
        # Характеристики питомца
        self.petHP = None
        # Игровые характеристики
        self.isPickUpDrop = False  # Признак сбора дропа
        self.lastHealTime = None  # Время последнего лечения
        self.lastPartyHealTime = None  # Время последнего лечения от членов группы
        self.lastAttackTime = None  # Время последнего вызова атаки
        self.lastAssistTime = None  # Время последнего вызова ассиста
        self.maxNoAttackInterval = 600  # Выход из программы, если персонаж не атакует цели указаное кол-во секунд
        self.needRebuff = False  # Признак необходимости бафнуться
        self.lastBuffTime = None  # Дата последнего ребафа
        self.buffInterval = 600  # Интервал для основного бафа (в секундах)
        self.needRegularBuff = False  # Признак необходимости применить регулярный бафф
        self.lastRegularBuffTime = None  # Дата последнего регулярного бафа
        self.regularBuffInterval = 83  # Интервал для регулярного бафа (в секундах)
        self.needDanceSong = False  # Признак необходимости использовать DanceSong
        self.lastDanceSongTime = None  # Дата последнего DanceSong
        self.danceSongInterval = 100  # Интервал DanceSong (в секундах)
        self.needChantOfVictory = False  # Признак необходимости использовать Chant of Victory
        self.lastChantOfVictoryTime = None  # Дата последнего Chant of Victory
        self.chantOfVictoryInterval = 280  # Интервал Chant of Victory (в секундах)
        self.allowSendCommand = True  # Разрешение на отправку команды членам группы
        self.fishingLine = None  # Текущая длина полоски рыбалки
        self.fishingPriorLine = None  # Предыдущая длина полоски рыбалки
        self.fishingLineInterval = 0.7  # Интервал обновления информации по длине полоски
        self.lastFishingLineTime = None  # Время последней проверки полоски рыбалки

    def printLog(self, text):
        """Запись лога в консоль"""
        date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        print("[%s]  %s" % (date, text))

    def start(self):
        """Запуск главного цикла бота"""
        self.isRunning = True
        if self.debugMode:
            self.printLog("Запущен режим отладки")
        # Запуск расширенной логики для различных видов перконажей
        self.startExtensions()
        # Создадим отдельный поток для работы бота
        thread_main = threading.Thread(target=self.main, args=[])
        thread_main.start()
        # Запустим клавиатуру
        self.virtualKeyboard.start()
        self.printLog("Клавиатура остановлена.")

    def startExtensions(self):
        """Запуск дополнительных расширений"""
        var = None

    def main(self):
        """Главный метод логики работы бота"""
        # Обратный отсчет (сек)
        self.countDown(5)
        while self.isRunning:
            self.commonActions()  # Выполнение общих действий

    def startRemoteServer(self):
        """"Запуск сервера для удаленного управления персонажами"""
        self.server = TeamServer()  # Инициализация сервера
        self.registerVirtualKeys()  # Резерирование NUM1-NUM9 для удаленного управления персонажами
        self.server.startServer()  # Запуск сервера

    def registerVirtualKeys(self):
        """Резертирование (регистрация) клавиш для удаленного управления персонажами"""
        self.virtualKeyboard.registerForKeyDown(self.virtualKeyboard.NUMERIC_1, self.server.eventPressedN1)
        self.virtualKeyboard.registerForKeyDown(self.virtualKeyboard.NUMERIC_2, self.server.eventPressedN2)
        self.virtualKeyboard.registerForKeyDown(self.virtualKeyboard.NUMERIC_3, self.server.eventPressedN3)
        self.virtualKeyboard.registerForKeyDown(self.virtualKeyboard.NUMERIC_4, self.server.eventPressedN4)
        self.virtualKeyboard.registerForKeyDown(self.virtualKeyboard.NUMERIC_5, self.server.eventPressedN5)
        self.virtualKeyboard.registerForKeyDown(self.virtualKeyboard.NUMERIC_6, self.server.eventPressedN6)
        self.virtualKeyboard.registerForKeyDown(self.virtualKeyboard.NUMERIC_7, self.server.eventPressedN7)
        self.virtualKeyboard.registerForKeyDown(self.virtualKeyboard.NUMERIC_8, self.server.eventPressedN8)
        self.virtualKeyboard.registerForKeyDown(self.virtualKeyboard.NUMERIC_9, self.server.eventPressedN9)
        self.printLog("Клавиши NUM1-NUM9 зарезервированы виртуальной клавиатурой.")

    def commonActions(self):
        """Общиие действия для всех видов персонажей"""
        # Сбор информации и вывод лога
        self.screen.refreshPrintScreen()
        self.getCharacterSpecifications()
        self.getTargetSpecifications()
        if self.debugMode:
            cv2.imshow('L2 Assistent Debug', self.screen.image)
            cv2.waitKey(1)

    def fishingActions(self):
        """Общие действия для рыбалки"""
        # Сбор информации и вывод лога
        self.screen.refreshPrintScreen()
        self.getCharacterSpecifications()
        self.getTargetSpecifications()
        self.screen.refreshPrintScreen()
        self.getFishingLine()
        self.mainFishing()
        if self.debugMode:
            cv2.imshow('L2 Assistent Debug', self.screen.image)
            cv2.waitKey(1)

    def questActions(self):
        """Общие действия для квеста"""
        self.virtualKeyboard.ESC.press()
        time.sleep(0.5)
        self.findQuestTarget()
        time.sleep(5)
        self.screen.refreshPrintScreen()
        self.getTargetSpecifications()
        if self.hasTarget:
            self.attackTarget()
            time.sleep(5)
            self.screen.refreshPrintScreen()
            self.pressQuest()
            time.sleep(1)
            self.screen.refreshPrintScreen()
            self.pressLookInside()
            time.sleep(1)

    def attackActions(self):
        """Действия для режима атаки"""
        if not self.attackMode:
            return

        if self.hasTarget:
            # Атаковать, если у цели есть шкала HP
            if self.targetHP is not None and self.targetHP > 0 or self.targetNoHP is not None and self.targetNoHP > 0:
                self.attackTarget()
                self.callAssist()
            # Закрыть цель, если это Игрок/NPC
            else:
                self.closeTarget()

        # Проверка на мертвую цель
        if self.hasTarget and self.targetHP == 0 and self.targetNoHP > 0:
            self.printLog("Цель мертва.")
            self.closeTarget()  # Сброс цели
            self.pickUpDrop()  # Поднятие дропа
            self.callFollowMe()  # Подозвать всех членов группы к себе

    def healActions(self):
        """Действия для самолечения"""
        if self.HP is not None and self.HP <= 75:
            now = time.time()
            # Если последнее лечение выполнялось более 10 секунд назад
            if self.lastHealTime is None or int(now - self.lastHealTime) >= 10:
                self.printLog("Самолечение.")
                self.selfHeal()
                self.lastHealTime = now

            if self.HP <= 65:
                # Лечение от членов группы
                if self.lastPartyHealTime is None or int(now - self.lastPartyHealTime) >= 10:
                    self.callHeal()

            if 1 <= self.HP <= 25:
                # Полное лечение если здоровье на критической отметке
                self.selfFullHeal()

    def findTargetActions(self):
        """Действия для поиска цели"""
        allow = self.checkAllowFindTarget()
        if not allow:
            return
        # Поиск ближайшей цели (например если атакуется пачка мобов)
        self.getNextTarget()
        self.screen.refreshPrintScreen()
        self.getTargetSpecifications()
        # Если ближайшая цель не найдена, то вызыватся макрос /target ...
        # У персонажа должно быть достаточно здоровья
        if not self.hasTarget and self.HP is not None and self.HP > 75:
            self.findNextTarget()

    def checkAllowFindTarget(self):
        """Проверка разрешения поиск цели"""
        # Не искать цель, если отключен режим атаки
        if not self.attackMode:
            return False
        # Не искать цель, если цель уже есть
        elif self.hasTarget:
            return False
        # Не искать цель, если требуется ребаф
        elif self.needRebuff:
            return False
        elif self.needRegularBuff:
            return False
        else:
            return True

    def rebuffActions(self):
        """Действия для Бафа"""
        now = time.time()
        if self.lastAttackTime is not None:
            attack_interval = now - self.lastAttackTime
        else:
            attack_interval = 999999

        self.needRebuff = (self.lastBuffTime is None) or (now - self.lastBuffTime) >= self.buffInterval
        self.needRegularBuff = (self.lastRegularBuffTime is None) or (
                    now - self.lastRegularBuffTime) >= self.regularBuffInterval
        self.needDanceSong = (self.lastDanceSongTime is None) or (
                    now - self.lastDanceSongTime) >= self.danceSongInterval
        self.needChantOfVictory = (self.lastChantOfVictoryTime is None) or (
                    now - self.lastChantOfVictoryTime) >= self.chantOfVictoryInterval

        if self.needRebuff:
            self.printLog("Требуется ребаф.")
            # Запустим ребаф, если с момента последней атаки прошло более 5 секунд
            if not self.hasTarget and attack_interval >= 5:
                self.reBuff()
                self.callBuff()
                # Подождем 5 секунд после ребафа
                time.sleep(5)
                return
        if self.needRegularBuff:
            self.printLog("Требуется регулярный бафф.")
            # Запустим регулярный баф, если нет цели
            if not self.hasTarget:
                self.regularBuff()
                self.lastRegularBuffTime = time.time()
                return
        if self.needChantOfVictory:
            self.callChantOfVictory()
            return
        if self.needDanceSong:
            self.callDanceSong()
            return

    def sendCommandToParty(self, command):
        """Отправка команд команде"""
        if self.server is not None and len(self.server.connectionList) > 0:
            self.server.sendToAll(command)

    def attackTarget(self):
        """Атаковать цель"""
        self.printLog("Атака цели.")
        self.lastAttackTime = time.time()  # Запомним время последней атаки
        if self.useKeyboard:
            self.virtualKeyboard.F1.press()
        else:
            self._findAndClickImageTemplate_(template='images/attack_button.png', threshold=0.8, image_count=1,
                                             cache=True)

        self.checkSuccessAttack()  # Проверка на успешную атаку цели

    def checkSuccessAttack(self):
        """Проверка на успешную атаку цели (на случай, если персонаж залип и не атакует цель)"""
        if self.targetHP is None:
            return
        # Запомним время старта атаки
        if self.startAttackTime is None:
            self.startAttackTime = time.time()
            self.everyTenSecondsTargetHP = self.targetHP
        # Каждые 10 секунд проверяем на сколько удачно цель атакуется
        else:
            total_attack_time = int(time.time() - self.startAttackTime)
            if total_attack_time < 10:
                return
            if total_attack_time % 10 == 0:
                if total_attack_time // 10 > self.currentTenSeconds:
                    # Если за последние 10 секунд здоровье цели не уменьшалось:
                    if self.everyTenSecondsTargetHP <= self.targetHP:
                        self.printLog("Цель не атакуется уже %s сек." % total_attack_time)
                        self.printLog("10 Секунд назад было %s ХП, а сейчас: %s." % (
                        str(self.everyTenSecondsTargetHP), str(self.targetHP)))
                        self.everyTenSecondsTry += 1
                        # Если цель не атакуется 30 секунд подряд
                        if self.everyTenSecondsTry >= 3:
                            self.printLog("Отмена цели.")
                            self.cancelTargetAndStepBack()  # Отменим цель и сделаем пару шагов назад
                    else:
                        self.everyTenSecondsTry = 0
                # Каждые 10 секунд запоминаем HP цели
                self.everyTenSecondsTargetHP = self.targetHP
                self.currentTenSeconds = total_attack_time // 10

    def cancelTargetAndStepBack(self):
        """Отменить цель и сделать пару шагов назад"""
        self.printLog("Персонаж застрял. Отмена цели.")
        self.closeTarget()
        self.virtualKeyboard.HOME.press()
        time.sleep(0.5)
        self.virtualKeyboard.DOWN_ARROW.down()
        time.sleep(1.5)
        self.virtualKeyboard.DOWN_ARROW.up()
        time.sleep(0.5)
        self.virtualKeyboard.UP_ARROW.press()

    def selfHeal(self):
        """Лечение"""
        if self.useKeyboard:
            self.virtualKeyboard.F5.press()
        else:
            self._findAndClickImageTemplate_(template='images/heal.png', threshold=0.8, image_count=1, cache=True)

    def selfFullHeal(self):
        """Вызов DanceSong"""
        self.printLog("Активация Полного лечения")
        if self.useKeyboard:
            self.blockKeyboard = True
            self.virtualKeyboard.LEFT_ALT.down()
            time.sleep(0.1)
            self.virtualKeyboard.N4.press()
            time.sleep(0.02)
            self.virtualKeyboard.LEFT_ALT.up()
            time.sleep(0.1)
            self.blockKeyboard = False
        else:
            self._findAndClickImageTemplate_(template='images/full_heal.png', threshold=0.8, image_count=1, cache=True)

    def reBuff(self):
        """Запуск ребафа"""
        self.printLog("Активация ребафа.")
        if self.useKeyboard:
            self.virtualKeyboard.LEFT_ALT.down()
            time.sleep(0.1)
            self.virtualKeyboard.N9.press()
            time.sleep(0.02)
            self.virtualKeyboard.LEFT_ALT.up()
            time.sleep(0.1)
        else:
            self._findAndClickImageTemplate_(template='images/buff_button.png', threshold=0.8, image_count=1,
                                             cache=True)

    def regularBuff(self):
        """Запуск регулярного бафа"""
        self.printLog("Активация регулярного бафа.")
        if self.useKeyboard:
            self.virtualKeyboard.F10.press()
        else:
            self._findAndClickImageTemplate_(template='images/regular_buff.png', threshold=0.8, image_count=1,
                                             cache=True)
        time.sleep(1)

    def danceSong(self):
        """Вызов DanceSong"""
        self.printLog("Активация DanceSong")
        if self.useKeyboard:
            self.virtualKeyboard.LEFT_ALT.down()
            time.sleep(0.1)
            self.virtualKeyboard.N0.press()
            time.sleep(0.02)
            self.virtualKeyboard.LEFT_ALT.up()
            time.sleep(0.1)
        else:
            self._findAndClickImageTemplate_(template='images/DanceSong.png', threshold=0.8, image_count=1, cache=True)

    def chantOfVictory(self):
        """Вызов Chant of Victory"""
        self.printLog("Активация Chant of Victory")
        if self.useKeyboard:
            self.virtualKeyboard.LEFT_ALT.down()
            time.sleep(0.1)
            self.virtualKeyboard.N6.press()
            time.sleep(0.02)
            self.virtualKeyboard.LEFT_ALT.up()
            time.sleep(0.1)
        else:
            self._findAndClickImageTemplate_(template='images/DanceSong.png', threshold=0.8, image_count=1, cache=True)

    def rebuffHunter(self):
        """Ребафф На сервере Hunter"""
        self.virtualKeyboard.ESC.press()
        time.sleep(0.5)
        self.virtualKeyboard.LEFT_ALT.down()
        time.sleep(0.5)
        self.virtualKeyboard.B.press()
        self.virtualKeyboard.LEFT_ALT.up()
        time.sleep(0.5)
        self.screen.refreshPrintScreen()
        self._findAndClickImageTemplate_(template='images/buffs.png', threshold=0.8, image_count=1)
        time.sleep(0.5)
        self.screen.refreshPrintScreen()
        self._findAndClickImageTemplate_(template='images/FullBuff.png', threshold=0.8, image_count=1)
        time.sleep(0.5)
        self.screen.refreshPrintScreen()
        self._findAndClickImageTemplate_(template='images/buff_all.png', threshold=0.8, image_count=1)
        time.sleep(0.5)

        self.virtualKeyboard.ESC.press()
        time.sleep(0.5)
        self.virtualKeyboard.LEFT_ALT.down()
        time.sleep(0.5)
        self.virtualKeyboard.B.press()
        self.virtualKeyboard.LEFT_ALT.up()
        time.sleep(0.5)
        self.screen.refreshPrintScreen()
        self._findAndClickImageTemplate_(template='images/buffs.png', threshold=0.8, image_count=1)
        time.sleep(0.5)
        self.screen.refreshPrintScreen()
        self._findAndClickImageTemplate_(template='images/DS.png', threshold=0.8, image_count=1)
        time.sleep(0.5)
        self.screen.refreshPrintScreen()
        self._findAndClickImageTemplate_(template='images/buff_all.png', threshold=0.8, image_count=1)
        time.sleep(0.5)
        self.virtualKeyboard.ESC.press()

    def assist(self):
        """Вызов Ассиста"""
        self.printLog("Ассист")
        if self.useKeyboard:
            self.virtualKeyboard.LEFT_ALT.down()
            time.sleep(0.1)
            self.virtualKeyboard.N8.press()
            time.sleep(0.02)
            self.virtualKeyboard.LEFT_ALT.up()
            time.sleep(0.1)
        else:
            self._findAndClickImageTemplate_(template='images/assist.png', threshold=0.8, image_count=1, cache=True)

    def followMe(self):
        """Призывает всех участников группы идти за лидером группы"""
        self.printLog("Идти за лидером группы.")
        if self.useKeyboard:
            self.virtualKeyboard.LEFT_ALT.down()
            time.sleep(0.1)
            self.virtualKeyboard.N7.press()
            time.sleep(0.02)
            self.virtualKeyboard.LEFT_ALT.up()
            time.sleep(0.1)
        else:
            self._findAndClickImageTemplate_(template='images/assist.png', threshold=0.8, image_count=1, cache=True)

    def checkCharacterDead(self):
        """Проверка на смерть персонажа"""
        areas = self.screen.findImageOnScreen(template='images/in_city.png', threshold=0.8, result_count=1, cache=False)
        self.isDead = len(areas) > 0

    def checkLastAttackTime(self):
        """Проверка на последнее время атаки. Если персонаж не атакует цели длительное время, то программа закроется"""
        now = time.time()
        if (self.lastAttackTime is not None) and (now - self.lastAttackTime >= self.maxNoAttackInterval):
            self.printLog("Персонаж не атакует цели уже %s сек." % self.maxNoAttackInterval)
            self.dispose()

    def exitIfDead(self):
        """Выход, если персонаж мертв"""
        if self.isDead:
            self.printLog("Персонаж мертв.")
            self.dispose()

    def getCharacterSpecifications(self):
        """Получить информацию о здоровье и мане персонажа"""
        areas = self.screen.findImageOnScreen(template='images/hp_bar_left.png', threshold=0.75, result_count=1,
                                              cache=True)
        if len(areas) > 0:
            area = areas[0]
            x1 = area['x1']
            x2 = area['x2'] + 158
            y1 = area['y1']
            y2 = area['y2']
            cropped = self.screen.image[y1:y2, x1:x2]
            if self.debugMode:
                cv2.rectangle(self.screen.image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            hp = self.screen.getContourColor(cropped, np.array([17, 15, 100], dtype="uint8"),
                                             np.array([50, 56, 200], dtype="uint8"))
            self.HP = self.screen.getPercents(hp, 152 - hp)
            mp = self.screen.getContourColor(cropped, np.array([134, 57, 5], dtype="uint8"),
                                             np.array([168, 81, 9], dtype="uint8"))
            self.MP = self.screen.getPercents(mp, 150 - mp)

        # Если не удалось обнаружить HP персонажа, то возможно он мертв
        if self.HP is not None and self.HP == 0:
            self.checkCharacterDead()

    def getTargetSpecifications(self):
        """Получение информации о Цели"""
        areas = self.screen.findImageOnScreen(template='images/target_bar_left.png', threshold=0.8, result_count=1,
                                              cache=False)
        if len(areas) > 0:
            area = areas[0]
            x1 = area['x1']
            x2 = area['x2'] + 168
            y1 = area['y1']
            y2 = area['y2']
            cropped = self.screen.image[y1:y2, x1:x2]
            if self.debugMode:
                cv2.rectangle(self.screen.image, (x1, y1), (x2, y2), (0, 0, 255), 2)
            # Сколько здоровья у цели осталось
            self.targetHP = self.screen.getContourColor(cropped, np.array([17, 15, 100], dtype="uint8"),
                                                        np.array([50, 56, 200], dtype="uint8"))
            # Сколько здоровья у цели отнято
            self.targetNoHP = self.screen.getContourColor(cropped, np.array([28, 30, 55], dtype="uint8"),
                                                          np.array([38, 40, 70], dtype="uint8"))
            self.hasTarget = True
        else:
            self.targetHP = None
            self.targetNoHP = None
            self.hasTarget = False

    def getFishingLine(self):
        """Получить информацию о полоске рыбалки"""
        areas = self.screen.findImageOnScreen(template='images/fishing_panel.png', threshold=0.75, result_count=1,
                                              cache=False)
        if len(areas) > 0:
            area = areas[0]
            x1 = area['x1']
            x2 = area['x2']
            y1 = area['y1']
            y2 = area['y2'] + 270
            cropped = self.screen.image[y1:y2, x1:x2]
            if self.debugMode:
                cv2.rectangle(self.screen.image, (x1, y1), (x2, y2), (0, 0, 255), 2)
            # line = self.screen.getContourColor(cropped, np.array([157, 105, 0], dtype="uint8"),
            #                                    np.array([242, 205, 130], dtype="uint8"))
            line = self.screen.getContourColor(cropped, np.array([157, 105, 0], dtype="uint8"),
                                               np.array([210, 165, 5], dtype="uint8"))
            self.fishingLine = line
        else:
            self.fishingLine = None
            self.fishingPriorLine = None
            self.lastFishingLineTime = None

    def getNextTarget(self):
        """Получение ближайшей цели (Нажатие макроса /nexttarget)"""

        self.printLog("Поиск ближейшей цели")
        if self.useKeyboard:
            self.virtualKeyboard.F11.press()
        else:
            self._findAndClickImageTemplate_(template='images/nexttarget_button.png', threshold=0.8, image_count=1,
                                             cache=True)
        time.sleep(0.25)

        self.screen.refreshPrintScreen()
        self.getTargetSpecifications()

    def findNextTarget(self):
        """Поиск ближайшей цели (Нажатие макроса /target ... )"""
        self.printLog("Использование макроса для поиска цели")
        if self.useKeyboard:
            self.virtualKeyboard.F12.press()
        else:
            self._findAndClickImageTemplate_(template='images/find_target.png', threshold=0.8, image_count=1,
                                             cache=True)
        time.sleep(0.25)
        self.screen.refreshPrintScreen()
        self.getTargetSpecifications()

    def mainFishing(self):
        """Главное тело логики рыбалки. Нажатие клавиш для фишинга"""
        # Алгоритм для процесса рыбалки
        if self.fishingLine is not None and self.fishingLine > 0:
            # Получим значение шкалы рыбалки 3 секунды ранее:
            if self.fishingPriorLine is None:
                self.fishingPriorLine = self.fishingLine
                self.lastFishingLineTime = time.time()
                self.printLog("Старт рыбалки...")

            if (time.time() - self.lastFishingLineTime) >= self.fishingLineInterval:
                # Если истек интервал проверки шкалы рыбалки
                if self.fishingLine > self.fishingPriorLine:
                    self.pressReeling()
                elif self.fishingLine == self.fishingPriorLine:
                    self.pressPumping()

                # Запомним текущее состояние шкалы рыбалки
                self.fishingPriorLine = self.fishingLine
                self.lastFishingLineTime = time.time()

        if self.fishingLine is None:
            if self.hasTarget is None or not self.hasTarget:
                # Поиск цели, если цель обнаружена
                self.getNextTarget()
                # Если цели всё равно нет, то продолжаем рыбачить
                if self.hasTarget is None or not self.hasTarget:
                    self.virtualKeyboard.F8.press()
                    self.virtualKeyboard.F7.press()
                    time.sleep(1)
                    self.virtualKeyboard.F10.press()
                    time.sleep(3)
            elif self.hasTarget is not None and self.hasTarget:
                # Если есть цель, то надеваем оружие и начинаем атаковать
                self.virtualKeyboard.F7.press()
                self.virtualKeyboard.F8.press()
                self.attackActions()

    def pressReeling(self):
        """Натиягивание лезки"""
        self.printLog("Использование макроса Натиягивания лезки")
        if self.useKeyboard:
            self.virtualKeyboard.F3.press()
        else:
            self._findAndClickImageTemplate_(template='images/reeling.png', threshold=0.8, image_count=1,
                                             cache=True)

    def pressPumping(self):
        """Подсечение рыбы"""
        self.printLog("Использование макроса Подсечения рыбы")
        if self.useKeyboard:
            self.virtualKeyboard.F2.press()
        else:
            self._findAndClickImageTemplate_(template='images/pumping.png', threshold=0.8, image_count=1,
                                             cache=True)

    def pickUpDrop(self, count=8):
        """Поднятие дропа (Нажатие клавиши F4),
        создается отдельный поток для сбора дропа"""
        thread_drop = threading.Thread(target=self._threadPickUpDrop_, args=[count])
        thread_drop.start()

    def _threadPickUpDrop_(self, count):
        """Поднятие дропа (Нажатие клавиши F4)"""
        self.isPickUpDrop = True
        for i in range(1, count):
            if not self.blockKeyboard:
                self.virtualKeyboard.F4.press()
                time.sleep(0.3)
        self.isPickUpDrop = False

    def blockSendCommand(self, seconds=10):
        """Блокировка отправки команд на указанное время в секундах"""
        thread_block = threading.Thread(target=self._threadBlockSendCommand_, args=[seconds])
        thread_block.start()

    def _threadBlockSendCommand_(self, seconds=10):
        """Блокировка отправления команд"""
        self.allowSendCommand = False
        time.sleep(seconds)
        self.allowSendCommand = True

    def closeTarget(self):
        """Сброс цели (нажатие клавиши ESC)"""
        self.virtualKeyboard.ESC.press()
        time.sleep(0.1)
        self.hasTarget = None
        self.targetHP = None
        self.targetNoHP = None
        self.startAttackTime = None
        self.everyTenSecondsTargetHP = None
        self.everyTenSecondsTry = 0
        self.currentTenSeconds = 0
        self.lastAssistTime = None

    def callAssist(self):
        """Вызов ассиста у членов группы"""
        if self.allowSendCommand:
            # Если с момента последнего ассиста прошло более 10 секунд
            now = time.time()
            if self.lastAssistTime is None or int(now - self.lastAssistTime) >= 10:
                self.sendCommandToParty("Assist")  # Вызов ассиста для членов группы
                self.lastAssistTime = now
                self.blockSendCommand(2)

    def callFollowMe(self):
        """Вызов всех членов группы к себе"""
        if self.allowSendCommand:
            self.sendCommandToParty("FollowMe")
            self.blockSendCommand(2)

    def callDanceSong(self):
        """Вызов Dance & Song для членов группы"""
        if self.allowSendCommand:
            # Если с момента последнего ассиста прошло более 10 секунд
            self.sendCommandToParty("DanceSong")
            self.lastDanceSongTime = time.time()
            self.blockSendCommand(6)

    def callChantOfVictory(self):
        """Вызов Chant Of Victory для членов группы"""
        if self.allowSendCommand:
            # Если с момента последнего ассиста прошло более 10 секунд
            self.sendCommandToParty("CoV")
            self.lastChantOfVictoryTime = time.time()
            self.blockSendCommand(2)

    def callBuff(self):
        """Вызов бафа от членов группы"""
        if self.allowSendCommand:
            self.sendCommandToParty("Buff")
            self.lastBuffTime = time.time()
            self.blockSendCommand(15)

    def callHeal(self):
        """Вызов хила от членов группы"""
        if self.allowSendCommand:
            self.sendCommandToParty("Heal")
            self.blockSendCommand(2)
            self.lastPartyHealTime = time.time()

    def _findAndClickImageTemplate_(self, template, threshold=0.8, image_count=1, cache=False):
        """Поиск и клик по изображению на экране"""
        areas = self.screen.findImageOnScreen(template=template, threshold=threshold, result_count=image_count,
                                              cache=cache)
        for area in areas:
            x = area['x_center']
            y = area['y_center']
            self.virtualKeyboard.mouse_move(x, y)
            time.sleep(0.1)
            self.virtualKeyboard.click_left_mouse()
            time.sleep(0.1)

    def pressOkTeamViewer(self):
        """Нажать OK в TeamViewer"""
        self._findAndClickImageTemplate_(template='images/teamviewer_ok.png', threshold=0.8, image_count=1,
                                         cache=False)

    def pressAccept(self):
        """Нажать кнопку "Принять" (Например принять торг)"""
        self.screen.refreshPrintScreen()
        # Запоминаем координаты курсора
        startX, startY = self.virtualKeyboard.getMousePosition()
        self._findAndClickImageTemplate_(template='images/accept.png', threshold=0.8, image_count=1,
                                         cache=False)
        # Возврат курсора на предыдущую координату
        self.virtualKeyboard.mouse_move(startX, startY)

    def pressYes(self):
        """Нажать кнопку "Да" (Например принять в группу)"""
        self.screen.refreshPrintScreen()
        # Запоминаем координаты курсора
        startX, startY = self.virtualKeyboard.getMousePosition()
        self._findAndClickImageTemplate_(template='images/yes.png', threshold=0.8, image_count=1,
                                         cache=False)
        # Возврат курсора на предыдущую координату
        self.virtualKeyboard.mouse_move(startX, startY)

    def pressQuest(self):
        """Нажать на кнопку "Задание(квест)" в диалоговом окне"""
        self.screen.refreshPrintScreen()
        # Запоминаем координаты курсора
        startX, startY = self.virtualKeyboard.getMousePosition()
        self._findAndClickImageTemplate_(template='images/quest.png', threshold=0.8, image_count=1,
                                         cache=False)
        # Возврат курсора на предыдущую координату
        self.virtualKeyboard.mouse_move(startX, startY)
        # Т.к. квест может быть написано по-разному, то проверим другой вариант кнопки
        self.screen.refreshPrintScreen()
        # Запоминаем координаты курсора
        startX, startY = self.virtualKeyboard.getMousePosition()
        self._findAndClickImageTemplate_(template='images/quest_rus.png', threshold=0.8, image_count=1,
                                         cache=False)
        # Возврат курсора на предыдущую координату
        self.virtualKeyboard.mouse_move(startX, startY)

    def pressLookInside(self):
        """Нажатие кнопки "Look Inside" (для квеста на саб-класс)"""
        self.screen.refreshPrintScreen()
        # Запоминаем координаты курсора
        startX, startY = self.virtualKeyboard.getMousePosition()
        self._findAndClickImageTemplate_(template='images/Look_inside.png', threshold=0.8, image_count=1,
                                         cache=False)
        # Возврат курсора на предыдущую координату
        self.virtualKeyboard.mouse_move(startX, startY)

    def findQuestTarget(self):
        """Поиск цели для квеста"""
        self.printLog("Использование макроса Поиска цели")
        if self.useKeyboard:
            self.virtualKeyboard.F8.press()
        else:
            self._findAndClickImageTemplate_(template='images/target_quest.png', threshold=0.8, image_count=1,
                                             cache=True)

    def stopAutoHotPy(self, autohotpy, event):
        """Остановка клавиатуры"""
        # Если нажат левый CTRL
        if self.virtualKeyboard.LEFT_CTRL.isPressed():
            self.dispose()

    def dispose(self):
        """Деструктор"""
        self.isRunning = False
        self.virtualKeyboard.LEFT_ALT.up()
        self.virtualKeyboard.stop()
        self.printLog("Отключение программы.")
        os._exit(1)

    def countDown(self, count):
        """Обратный отсчет"""
        for i in range(0, count):
            self.printLog("Осталось %s сек. до старта" % (count - i))
            time.sleep(1)
            if not self.isRunning:
                break
