# Библиотеки для управления виртуальной клавиатурой и мышью
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
        # Характеристики персонажа
        self.HP = None
        self.MP = None
        self.CP = None
        self.isDead = False
        # Характеристики цели
        self.hasTarget = None  # Признак наличия цели
        self.targetHP = None  # Количество пикселей со здоровьем Цели
        self.targetNoHP = None  # Количество пикселей с отсутствующим здоровьем цели
        # Характеристики питомца
        self.petHP = None
        # Игровые характеристики
        self.isPickUpDrop = False  # Признак сбора дропа
        self.lastHealTime = None  # Время последнего лечения
        self.lastAttackTime = None  # Время последнего вызова атаки
        self.needRebuff = False  # Признак необходимости бафнуться
        self.lastBuffTime = None  # Дата последнего ребафа
        self.buffInterval = 600  # Интервал для основного бафа (в секундах)
        self.needRegularBuff = False  # Признак необходимости применить регулярный бафф
        self.lastRegularBuffTime = None  # Дата последнего регулярного бафа
        self.regularBuffInterval = 83  # Интервал для регулярного бафа (в секундах)
        self.needDanceSong = False  # Признак необходимости использовать DanceSong
        self.lastDanceSongTime = None  # Дата последнего DanceSong
        self.danceSongInterval = 100  # Интервал DanceSong (в секундах)

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

    def attackActions(self):
        """Действия для режима атаки"""
        if not self.attackMode:
            return
        # Проверка на мертвую цель
        if self.hasTarget and self.targetHP == 0 and self.targetNoHP > 0:
            self.printLog("Цель мертва.")
            self.closeTarget()  # Сброс цели
            self.pickUpDrop()  # Поднятие дропа

        # Если уровень HP цели больше 0 или цель уже атаковалась
        if self.hasTarget:
            if self.targetHP is not None and self.targetHP > 0 or self.targetNoHP is not None and self.targetNoHP > 0:
                self.attackTarget()
            else:
                self.closeTarget()

    def healActions(self):
        """Действия для самолечения"""
        if self.HP is not None and self.HP <= 75:
            now = time.time()
            # Если последнее лечение выполнялось более 10 секунд назад
            if self.lastHealTime is None or int(now - self.lastHealTime) >= 10:
                self.printLog("Самолечение.")
                self.selfHeal()
                self.lastHealTime = now

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
        else:
            return True

    def rebuffActions(self):
        """Действия для Бафа"""
        now = time.time()
        if self.lastAttackTime is not None:
            attack_interval = now-self.lastAttackTime
        else:
            attack_interval = 99999

        self.needRebuff = (self.lastBuffTime is None) or (now - self.lastBuffTime) >= self.buffInterval
        self.needRegularBuff = (self.lastRegularBuffTime is None) or (now - self.lastRegularBuffTime) >= self.regularBuffInterval
        self.needDanceSong = (self.lastDanceSongTime is None) or (now - self.lastDanceSongTime) >= self.danceSongInterval

        if self.needRebuff:
            self.printLog("Требуется ребаф.")
            # Запустим ребаф, если с момента последней атаки прошло более 10 секунд
            if not self.hasTarget and attack_interval >= 10:
                self.reBuff()
                self.lastBuffTime = time.time()

        if self.needRegularBuff:
            self.printLog("Требуется регулярный бафф.")
            # Запустим регулярный баф, если нет цели
            if not self.hasTarget:
                self.regularBuff()
                self.lastRegularBuffTime = time.time()
        # if self.needDanceSong:
        #     self.printLog("Требуется DanceSong.")

    def attackTarget(self):
        """Атаковать цель"""
        self.printLog("Атака цели.")
        self.lastAttackTime = time.time()  # Запомним время последней атаки
        if self.useKeyboard:
            self.virtualKeyboard.F1.press()
        else:
            self._findAndClickImageTemplate_(template='images/attack_button.png', threshold=0.8, image_count=1, cache=True)

    def selfHeal(self):
        """Лечение"""
        if self.useKeyboard:
            self.virtualKeyboard.F5.press()
        else:
            self._findAndClickImageTemplate_(template='images/heal.png', threshold=0.8, image_count=1, cache=True)

    def reBuff(self):
        """Запуск ребафа"""
        self.printLog("Активация ребафа.")
        self._findAndClickImageTemplate_(template='images/buff_button.png', threshold=0.8, image_count=1, cache=True)

    def regularBuff(self):
        """Запуск регулярного бафа"""
        self.printLog("Активация регулярного бафа.")
        self._findAndClickImageTemplate_(template='images/regular_buff.png', threshold=0.8, image_count=1, cache=True)

    def checkCharacterDead(self):
        """Проверка на смерть персонажа"""
        areas = self.screen.findImageOnScreen(template='images/in_city.png', threshold=0.8, result_count=1, cache=False)
        self.isDead = len(areas) > 0

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
        areas = self.screen.findImageOnScreen(template='images/target_bar_left.png', threshold=0.8, result_count=1, cache=False)
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
            self.targetHP = self.screen.getContourColor(cropped, np.array([17, 15, 100], dtype="uint8"), np.array([50, 56, 200], dtype="uint8"))
            # Сколько здоровья у цели отнято
            self.targetNoHP = self.screen.getContourColor(cropped, np.array([28, 30, 55], dtype="uint8"), np.array([38, 40, 70], dtype="uint8"))
            self.hasTarget = True
        else:
            self.targetHP = None
            self.targetNoHP = None
            self.hasTarget = False

    def getNextTarget(self):
        """Получение ближайшей цели (Нажатие макроса /nexttarget)"""
        self.printLog("Поиск ближейшей цели")
        if self.useKeyboard:
            self.virtualKeyboard.F11.press()
        else:
            self._findAndClickImageTemplate_(template='images/nexttarget_button.png', threshold=0.8, image_count=1, cache=True)
        time.sleep(0.25)
        self.screen.refreshPrintScreen()
        self.getTargetSpecifications()

    def findNextTarget(self):
        """Поиск ближайшей цели (Нажатие макроса /target ... )"""
        self.printLog("Использование макроса для поиска цели")
        if self.useKeyboard:
            self.virtualKeyboard.F12.press()
        else:
            self._findAndClickImageTemplate_(template='images/find_target.png', threshold=0.8, image_count=1, cache=True)
        time.sleep(0.25)
        self.screen.refreshPrintScreen()
        self.getTargetSpecifications()

    def pickUpDrop(self, count=8):
        """Поднятие дропа (Нажатие клавиши F4),
        создается отдельный поток для сбора дропа"""
        thread_drop = threading.Thread(target=self._threadPickUpDrop_, args=[count])
        thread_drop.start()

    def closeTarget(self):
        """Сброс цели (нажатие клавиши ESC)"""
        self.virtualKeyboard.ESC.press()
        time.sleep(0.1)
        self.hasTarget = None
        self.targetHP = None
        self.targetNoHP = None

    def _threadPickUpDrop_(self, count):
        self.isPickUpDrop = True
        for i in range(1, count):
            self.virtualKeyboard.F4.press()
            time.sleep(0.2)
        self.isPickUpDrop = False

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
        self._findAndClickImageTemplate_(template='images/accept.png', threshold=0.8, image_count=1,
                                         cache=False)

    def pressYes(self):
        """Нажать кнопку "Да" (Например принять в группу)"""
        self.screen.refreshPrintScreen()
        self._findAndClickImageTemplate_(template='images/yes.png', threshold=0.8, image_count=1,
                                         cache=False)

    def stopAutoHotPy(self, autohotpy, event):
        """Остановка клавиатуры"""
        # Если нажат левый CTRL
        if self.virtualKeyboard.LEFT_CTRL.isPressed():
            self.dispose()

    def dispose(self):
        """Деструктор"""
        self.isRunning = False
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