# Общий класс управления персонажами
from libs.character import Character


class Fighter(Character):
    """Класс управления воином, унаследован от общего класса: Character"""

    def main(self):
        """Главный метод логики работы бота"""
        # Обратный отсчет (сек)
        self.countDown(10)
        self.pressOkTeamViewer()  # Нажатие ОК в TeamViewer
        while self.isRunning:
            self.commonActions()  # Выполнение общих действий
            self.rebuffActions()  # Выполнение действий для бафа
            self.attackActions()  # Выполнение действий для атаки
            self.findTargetActions()  # Выполнение действий для поиска цели
            self.healActions()  # Выполнение действий для самолечения
            self.exitIfDead()  # Выход из программы, если персонаж мерт
            self.checkLastAttackTime()  # Выход из программы, если персонаж не атакует цели длительное времч

    def startExtensions(self):
        """Запуск расширений"""
        super().startExtensions()
        self.startRemoteServer()  # Запуск сервера для удаленного управления персонажами
