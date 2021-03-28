# Общий класс управления персонажами
from libs.character import Character


class Assister(Character):
    """Класс управления персонажем на удаленном узле который работает по ассисту"""

    def main(self):
        """Главный метод логики работы бота"""
        # Обратный отсчет (сек)
        self.countDown(6)
        self.pressOkTeamViewer()  # Нажатие ОК в TeamViewer
        while self.isRunning:
            self.commonActions()  # Выполнение общих действий
            self.assisterActions()  # Выполнение действий для ассиста