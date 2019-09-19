"""Запуск управления персонажем атакующего типа для фарма"""
from libs.fisher import Fisher

la2Character = Fisher(debug_mode=False, attack_mode=False)
la2Character.start()
