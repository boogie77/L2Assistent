import cv2
import pyautogui
import numpy as np


class ScreenTools(object):
    """Класс для работы с экраном. Функции: получение скриншота экрана, поиск элемента на экране"""

    def __init__(self):
        self.cache = {}  # Внутренний кэш

    def getAttribute(self, attribute_key):
        """Получить значение из кэша"""
        return self.cache[attribute_key] if attribute_key in self.cache else None

    def setAttribute(self, attribute_key, attribute_value):
        """Задать значение в кэш"""
        self.cache[attribute_key] = attribute_value

    def getPrintScreen(self):
        """Делает скриншот экрана, возвращает в цвете и в ЧБ"""
        image = pyautogui.screenshot()
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image, image_grey

    def findImageOnScreen(self, image_grey, template, threshold, result_count=1, cache=False):
        """Функция поиска изображения по шаблону на сриншоте экрана"""
        result = []
        found_object = {}
        # Загрузка шаблона из файла или из кэша
        if template in self.cache:
            template_image = self.getAttribute(template)
        else:
            template_image = cv2.imread(template, 0)
            self.setAttribute(template, template_image)

        # Результат найденного изображения берем из кэша, если параметр cache == True
        result_cache_name = template + '_objects'
        if cache:
            result = self.getAttribute(result_cache_name)
        if cache and result is not None:
            return result
        else:
            result = []
            w, h = template_image.shape[::-1]
            res = cv2.matchTemplate(image_grey, template_image, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= threshold)
            for pt in zip(*loc[::-1]):
                x1 = pt[0]
                x2 = pt[0] + w
                y1 = pt[1]
                y2 = pt[1] + h
                x_center = round(x1 + (x2 - x1) / 2)
                y_center = round(y1 + (y2 - y1) / 2)
                found_object.clear()
                found_object['x1'] = x1
                found_object['x2'] = x2
                found_object['y1'] = y1
                found_object['y2'] = y2
                found_object['x_center'] = x_center
                found_object['y_center'] = y_center
                result.append(found_object)
                if result_count == result_count:
                    break
            # Результат найденного изображения кладем в кэш, если параметр cache == True
            self.setAttribute(result_cache_name, result)

        return result
