"""Запуск управления персонажем атакующего типа для фарма"""
from libs.remote_character import RemoteCharacter

la2Character = RemoteCharacter(debug_mode=False, attack_mode=False)
la2Character.start()
