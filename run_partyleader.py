"""Запуск управления персонажем атакующего типа для фарма с управлением персонажами на удаленных узлах"""
from libs.partyleader import PartyLeader

la2Character = PartyLeader(debug_mode=False)
la2Character.start()
