import cv2
# import d3dshot
import pyautogui
import numpy as np


class ScreenTools(object):
    """Класс для работы с экраном. Функции: получение скриншота экрана, поиск элемента на экране"""

    def __init__(self):
        self.cache = {}  # Внутренний кэш
        # self.d3d = d3dshot.create(capture_output="numpy")  # Инициализация функции захвата экрана
        self.image, self.image_grey = self.getPrintScreen()  # Сохранение скриншота экрана

    def getAttribute(self, attribute_key):
        """Получить значение из кэша"""
        return self.cache[attribute_key] if attribute_key in self.cache else None

    def setAttribute(self, attribute_key, attribute_value):
        """Задать значение в кэш"""
        self.cache[attribute_key] = attribute_value

    def refreshPrintScreen(self):
        """Обновляет глобальные переменные со снимком экрана"""
        self.image, self.image_grey = self.getPrintScreen()

    def getPrintScreen(self):
        """Делает скриншот экрана, возвращает в цвете и в ЧБ"""
        # image = self.d3d.screenshot()  # Скриншот с помощью D3D
        image = pyautogui.screenshot()  # Скриншот с помощью pyautogui
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image, image_grey

    def findImageOnScreen(self, template, threshold=0.8, result_count=1, cache=False):
        """Функция поиска изображения по шаблону на сриншоте экрана,
        template - путь до файла с искомым изображением;
        threshold - точность в процентах (где 1 = 100%), с которой функцяи вернет результат;
        result_count - количество искомых объектов;
        cache - кэшировать ли результат"""
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
            res = cv2.matchTemplate(self.image_grey, template_image, cv2.TM_CCOEFF_NORMED)
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
                if len(result) == result_count:
                    break
            # Результат найденного изображения кладем в кэш, если параметр cache == True
            self.setAttribute(result_cache_name, result)

        return result

    def getContourColor(self, img, lower, upper):
        """Получить длину контура в изображении (необходимо для расчета количества ХП, МП, ЦП)"""
        # Поиск объекта по маске (цветовой диапазон)
        mask = cv2.inRange(img, lower, upper)
        output = cv2.bitwise_and(img, img, mask=mask)

        # Наложение фильтров для лучшего чтения
        ret, threshold1 = cv2.threshold(output, lower[2], upper[2], cv2.THRESH_BINARY)
        closed_grey = cv2.cvtColor(threshold1, cv2.COLOR_BGR2GRAY)
        (arrays, _) = cv2.findContours(closed_grey.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        min_x = None
        max_x = None
        if len(arrays) > 0:
            for array in arrays:
                for point in array:
                    if min_x is None:
                        min_x = point[0][0]
                    if max_x is None:
                        max_x = point[0][0]
                    if min_x > point[0][0]:
                        min_x = point[0][0]
                    if max_x < point[0][0]:
                        max_x = point[0][0]
            if min_x is not None and max_x is not None:
                result = max_x - min_x
            else:
                result = 0
        else:
            result = 0

        return result

    def getContourColorByMask(self, img, lower, upper):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        cnts, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        if len(cnts) == 0:
            return 0
        else:
            return np.amax(cnts[0], axis=0)[0][0]

    # Получить процентное соотношение
    def getPercents(self, a, b):
        try:
            result = round(a / (a + b) * 100, 0)
        except Exception as e:
            result = None
        return result
