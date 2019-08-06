import socket
import os
import threading
from datetime import datetime


def getExternalIP():
    """Получение внешнего IP адреса"""
    external_ip = None
    try:
        external_ip = os.popen('curl -s ifconfig.me').readline()
    except Exception as x:
        print("Не удалось получить внешний IP адрес, ", x)
    return external_ip


def printLog(text):
    """Запись лога в консоль"""
    date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    print("[%s]  %s" % (date, text))


class TeamServer(object):
    """Сервер для удаленного управления персонажами"""

    def __init__(self):
        # Список подключений
        self.connectionList = {}
        # Инициализация сокета
        self.ser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Атрибуты для настроек
        self.HOST = ''
        self.PORT = 5023
        self.ser_sock.bind((self.HOST, self.PORT))
        # Получим внешний адрес для подключения
        self.externalIP = getExternalIP()

    def startServer(self):
        """Запуск сервера и считывание подключений по порту"""
        printLog("Запуск сервера")
        self.ser_sock.listen(1)
        thread_ac = threading.Thread(target=self.acceptClient)
        thread_ac.start()
        printLog("Сервер IP: %s" % self.externalIP)
        printLog("Сервер PORT: %s" % self.PORT)

    def acceptClient(self):
        """Прием подключений клиентов"""
        while True:
            # accept
            cli_sock, cli_add = self.ser_sock.accept()
            self.connectionList[cli_add] = cli_sock
            txt = '%s подключился к серверу. Всего подключено: %s' % (str(cli_add), str(len(self.connectionList)))
            printLog(txt)

    def sendToAll(self, message):
        """Отправка команд всем клиентам"""
        printLog("Отправка комманды: %s" % message)
        for i in list(self.connectionList):
            try:
                client = self.connectionList[i]
                client.send(message.encode())
            except Exception as x:
                printLog('%s отключился по причине: %s' % (i, x))
                try:
                    del self.connectionList[i]
                except KeyError:
                    printLog('Ключ %s не найден.' % i)

    def _buildMessageText_(self, keyboard, event, message):
        """Формирование текста сообщения в зависимости от нажатых клавиш"""
        command = message
        if keyboard.LEFT_ALT.isPressed():
            command = 'alt+' + command
        if keyboard.LEFT_CTRL.isPressed():
            command = 'ctrl+' + command
        return command

    def eventPressedN1(self, keyboard, event):
        """Событие при нажатии NUM 1"""
        self.sendToAll(self._buildMessageText_(keyboard=keyboard, event=event, message="F1"))

    def eventPressedN2(self, keyboard, event):
        """Событие при нажатии NUM 2"""
        self.sendToAll(self._buildMessageText_(keyboard=keyboard, event=event, message="F2"))

    def eventPressedN3(self, keyboard, event):
        """Событие при нажатии NUM 3"""
        self.sendToAll(self._buildMessageText_(keyboard=keyboard, event=event, message="F3"))

    def eventPressedN4(self, keyboard, event):
        """Событие при нажатии NUM 4"""
        self.sendToAll(self._buildMessageText_(keyboard=keyboard, event=event, message="F4"))

    def eventPressedN5(self, keyboard, event):
        """Событие при нажатии NUM 5"""
        self.sendToAll(self._buildMessageText_(keyboard=keyboard, event=event, message="F5"))

    def eventPressedN6(self, keyboard, event):
        """Событие при нажатии NUM 6"""
        self.sendToAll(self._buildMessageText_(keyboard=keyboard, event=event, message="F6"))

    def eventPressedN7(self, keyboard, event):
        """Событие при нажатии NUM 7"""
        self.sendToAll(self._buildMessageText_(keyboard=keyboard, event=event, message="F7"))

    def eventPressedN8(self, keyboard, event):
        """Событие при нажатии NUM 8"""
        self.sendToAll(self._buildMessageText_(keyboard=keyboard, event=event, message="F8"))

    def eventPressedN9(self, keyboard, event):
        """Событие при нажатии NUM 9"""
        self.sendToAll(self._buildMessageText_(keyboard=keyboard, event=event, message="F9"))

