# Библиотеки для управления виртуальной клавиатурой и мышью
from AutoHotPy import AutoHotPy
# Библиотека для захвата и анализа экрана
from libs.screen import ScreenTools
# Системные библиотеки
import os
import time
import numpy as np
import cv2


class Character(object):
    """Класс описывает свойства и методы управления персонажем"""

    def __init__(self):
        # Константы
        self.useKeyboard = True  # Использование клавиатуры вместо мыши для нажатия на макросы
        self.debugMode = False  # Режим отладки
        # Дополнительные объекты
        self.virtualKeyboard = AutoHotPy()  # Виртуальная клавиатура
        self.screen = ScreenTools()  # Средство анализа экрана
        # Характеристики персонажа
        self.HP = None
        self.MP = None
        self.CP = None
        self.isDead = False
        # Характеристики цели
        self.hasTarget = None
        self.targetHP = None
        # Характеристики питомца
        self.petHP = None

    def printLog(self):
        """Запись лога в консоль"""
        pad_spaces = 30
        _ = os.system('cls')
        print("-----------------------------------------------------------------")
        print(" Общая информация")
        print(" ")
        print(" HP:".ljust(pad_spaces), self.HP, "%")
        print(" MP:".ljust(pad_spaces), self.MP, "%")
        print(" Pet HP:".ljust(pad_spaces), self.petHP, "%")
        print(" Has target:".ljust(pad_spaces), self.hasTarget)
        print(" Target HP:".ljust(pad_spaces), self.targetHP)
        print("-----------------------------------------------------------------")

    def checkCharacterDead(self):
        """Проверка на смерть персонажа"""
        areas = self.screen.findImageOnScreen(template='img/in_city.png', threshold=0.8, result_count=1, cache=False)
        self.isDead = len(areas) > 0

    def getCharacterSpecifications(self):
        """Получить информацию о здоровье и мане персонажа"""
        areas = self.screen.findImageOnScreen(template='img/hp_bar_left.png', threshold=0.75, result_count=1,
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

    def _findAndClickImageTemplate_(self, template='img/teamviewer_ok.png', threshold=0.8, image_count=1, cache=False):
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
        self._findAndClickImageTemplate_(template='img/teamviewer_ok.png', threshold=0.8, image_count=1,
                                         cache=False)
