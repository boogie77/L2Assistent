"""Запуск управления персонажем атакующего типа для фарма"""
from libs.fighter import Fighter

la2Character = Fighter(debug_mode=False, attack_mode=True)
la2Character.start()
