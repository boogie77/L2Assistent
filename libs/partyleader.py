# Общий класс управления персонажами
from libs.character import Character


class PartyLeader(Character):
    """Класс позволяющий управлять удаленно персонажами с помощью нажатий клавиш NUM1-NUM9, унаследован от общего класса: Character"""

    def main(self):
        """Главный метод логики работы бота"""
        self.printLog("Готов к передаче команд.")

    def startExtensions(self):
        """Запуск расширений"""
        super().startExtensions()
        self.startRemoteServer()  # Запуск сервера для удаленного управления персонажами
