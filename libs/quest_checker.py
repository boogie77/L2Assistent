# Общий класс управления персонажами
from libs.character import Character


class QuestChecker(Character):
    """Класс управления персонажем для поиска квестового NPC и нажатия кнопки QUEST.
    Подходит для квеста на саб-класс.
    Унаследован от общего класса: Character"""

    def main(self):
        """Главный метод логики работы бота"""
        # Обратный отсчет (сек)
        self.countDown(5)
        self.pressOkTeamViewer()  # Нажатие ОК в TeamViewer
        while self.isRunning:
            self.commonActions()  # Выполнение общих действий
            self.healActions()  # Выполнение действий для самолечения
            self.questActions()  # Выполнение общих действий для квеста
