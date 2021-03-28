"""Запуск удаленного управления персонажем атакующего типа для фарма на нескольких компьютеров"""
from libs.assister import Assister

la2Character = Assister(debug_mode=False, attack_mode=True)
la2Character.start()
