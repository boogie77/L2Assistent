# Общий класс управления персонажами
from libs.character import Character


class Fighter(Character):
    """Класс управления воином, унаследован от общего класса: Character"""

    def main(self):
        """Главный метод логики работы бота"""
        # Обратный отсчет (сек)
        self.countDown(5)
        while self.isRunning:
            self.commonActions()  # Выполнение общих действий
            self.attackActions()  # Выполнение действий для атаки
            self.findTargetActions()  # Выполнение действий для поиска цели
            self.healActions()  # Выполнение действий для самолечения
