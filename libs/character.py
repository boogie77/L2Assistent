# Библиотеки для управления виртуальной клавиатурой и мышью
from AutoHotPy import AutoHotPy
# Библиотека для захвата и анализа экрана
from libs.screen import ScreenTools
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
        # Характеристики персонажа
        self.HP = None
        self.MP = None
        self.CP = None
        self.isDead = False
        # Характеристики цели
        self.hasTarget = None
        self.targetHP = None  # Количество пикселей со здоровьем Цели
        self.targetNoHP = None  # Количество пикселей с отсутствующим здоровьем цели
        # Характеристики питомца
        self.petHP = None
        # Игровые характеристики
        self.isPickUpDrop = False  # Признак сбора дропа
        self.lastHealTime = None  # Время последнего лечения

    def main(self):
        """Главный метод логики работы бота"""
        # Обратный отсчет (сек)
        self.countDown(5)
        while self.isRunning:
            self.commonActions()  # Выполнение общих действий

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
        # Проверка на мертвую цель
        if self.hasTarget and self.targetHP == 0 and self.targetNoHP > 0:
            self.printLog("Цель мертва.")
            self.closeTarget()  # Сброс цели
            self.pickUpDrop()  # Поднятие дропа

        # Если уровень HP цели больше 0 или цель уже атаковалась
        if self.hasTarget:
            if self.targetHP > 0 or self.targetNoHP > 0:
                self.attackTarget()
            else:
                self.closeTarget()

    def healActions(self):
        """Действия для самолечения"""
        if self.HP <= 75:
            now = time.time()
            # Если последнее лечение выполнялось более 10 секунд назад
            if self.lastHealTime is None or int(now - self.lastHealTime) >= 10:
                self.printLog("Самолечение.")
                self.selfHeal()
                self.lastHealTime = now

    def findTargetActions(self):
        """Действия для поиска цели"""
        if self.hasTarget:
            return
        # Поиск ближайшей цели (например если атакуется пачка мобов)
        self.getNextTarget()
        self.screen.refreshPrintScreen()
        self.getTargetSpecifications()
        # Если ближашая цель не найдена, то вызыватся макрос /target ...
        # У персонажа должно быть достаточно здоровья
        if not self.hasTarget and self.HP > 75:
            self.findNextTarget()

    def attackTarget(self):
        """Атаковать цель"""
        self.printLog("Атака цели.")
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

    def printLog(self, text):
        """Запись лога в консоль"""
        date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        print("[%s]  %s" % (date, text))

    def checkCharacterDead(self):
        """Проверка на смерть персонажа"""
        areas = self.screen.findImageOnScreen(template='images/in_city.png', threshold=0.8, result_count=1, cache=False)
        self.isDead = len(areas) > 0

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
            self.targetHP = self.screen.getContourColor(cropped, np.array([17, 15, 100], dtype="uint8"), np.array([50, 56, 200], dtype="uint8"))
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

    def start(self):
        """Запуск главного цикла бота"""
        self.isRunning = True
        if self.debugMode:
            self.printLog("Запущен режим отладки")
        # Создадим отдельный поток для работы бота
        thread_main = threading.Thread(target=self.main, args=[])
        thread_main.start()
        # Запустим клавиатуру
        self.virtualKeyboard.start()
        self.printLog("Клавиатура остановлена.")

    def stopAutoHotPy(self, autohotpy, event):
        """Остановка клавиатуры"""
        # Если нажат левый CTRL
        if self.virtualKeyboard.LEFT_CTRL.isPressed():
            self.virtualKeyboard.stop()
            self.isRunning = False
            self.printLog("Клавиатура будет остановлена.")

    def countDown(self, count):
        """Обратный отсчет"""
        for i in range(0, count):
            self.printLog("Осталось %s сек. до старта" % (count - i))
            time.sleep(1)
            if not self.isRunning:
                break

    def dispose(self):
        """Деструктор"""
        self.isRunning = False
        self.virtualKeyboard.stop()
        os._exit(1)
