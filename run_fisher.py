"""Запуск управления персонажем атакующего типа для фарма"""
from libs.fisher import Fisher

la2Character = Fisher(debug_mode=False, attack_mode=True)
la2Character.start()
