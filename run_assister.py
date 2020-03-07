"""Запуск управления персонажем атакующего типа для фарма"""
from libs.assister import Assister

la2Character = Assister(debug_mode=False, attack_mode=True)
la2Character.start()
