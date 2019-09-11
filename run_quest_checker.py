"""Запуск управления персонажем атакующего типа для фарма"""
from libs.quest_checker import QuestChecker

la2Character = QuestChecker(debug_mode=False, attack_mode=False)
la2Character.start()
