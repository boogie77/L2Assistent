# Общий класс управления персонажами
from libs.character import Character


class Fisher(Character):
    """Класс управления воином, унаследован от общего класса: Character"""

    def main(self):
        """Главный метод логики работы бота"""
        # Обратный отсчет (сек)
        self.countDown(5)
        self.pressOkTeamViewer()  # Нажатие ОК в TeamViewer
        while self.isRunning:
            self.fishingActions()  # Действия для рыбалки
