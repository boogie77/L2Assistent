# Общий класс управления персонажами
from libs.character import Character
import win32gui
import win32com.client
import socket
import configparser
import threading
import time


class RemoteCharacter(Character):
    """Класс позволяющий принимать и выполнять команды с удаленного сервера, унаследован от общего класса: Character"""

    def __init__(self, debug_mode=False, attack_mode=False):
        self.connected = False  # Признак подключения к серверу
        self.winList = []  # Список окон с игрой
        self.ServerHost = '127.0.0.1'  # Адрес сервера
        self.ServerPort = '5023'  # Порт сервера
        self.windowName = 'asterios '

        # Вызов метода из родительского класса
        super().__init__(debug_mode=debug_mode, attack_mode=attack_mode)

        # Инициализация сокета
        self.cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Shell необходим для обхода ошибки переключения окон win32com
        self.shell = win32com.client.Dispatch("WScript.Shell")
        self.shell.SendKeys('%')

    def main(self):
        """Главный метод логики работы бота"""
        self.printLog("Ожидание команд...")

    def startExtensions(self):
        """Запуск расширений"""
        super().startExtensions()
        self.startRemoteClient()

    def startRemoteClient(self):
        """Запуск клиента для чтения команд с сервера"""
        self.connectToServer()
        self.startListenServer()

    def startListenServer(self):
        """Создание потока для считывания команд сервера"""
        thread_receive = threading.Thread(target=self.listenServer, args=[])
        thread_receive.start()

    def listenServer(self):
        """Чтение команд от сервера"""
        try:
            while self.connected:
                # Чтение комманды
                data = self.cli_sock.recv(1024)
                message = str(data.decode())
                commands = message.split('+')
                self.printLog("Получена команда: %s" % str(commands))

                # Получим список окон
                self.winList = []
                top_list = []
                win32gui.EnumWindows(self._get_windows_list_, top_list)
                programs = [(hwnd, title) for hwnd, title in self.winList if self.windowName in title.lower()]
                # Развернем окно с игрой и выполним действие
                for program in programs:
                    try:
                        # Разворот окна
                        self.shell.SendKeys('%')
                        win32gui.SetForegroundWindow(program[0])
                        # Нажатие клавиши
                        self.executeCommandsFromServer(commands)
                    except Exception as x:
                        self.printLog(x)
        except ConnectionResetError:
            self.connected = False
            self.printLog("Соединение с сервером было разорвано.")
            self.dispose()

    def _get_windows_list_(self, hwnd, results):
        """Получение списка окон"""
        self.winList.append((hwnd, win32gui.GetWindowText(hwnd)))

    def connectToServer(self):
        """Подключение к удаленному серверу """
        # Загрузим подключение из конфигурационного INI файла
        config = configparser.ConfigParser()
        config.read('settings.ini')
        try:
            self.ServerHost = config.get('ServerInfo', 'HOST')
            self.ServerPort = config.get('ServerInfo', 'PORT')
        except Exception as x:
            config.add_section('ServerInfo')
            self.ServerHost = None
            self.ServerPort = None

        if self.ServerHost is None:
            self.ServerHost = '127.0.0.1'
        if self.ServerPort is None:
            self.ServerPort = '5023'
        input_host = input('Введите HOST сервера или нажмите ENTER для сохранение настроек по-умолчанию (' + str(self.ServerHost) + ') : ')
        input_port = input('Введите PORT сервера или нажмите ENTER для сохранение настроек по-умолчанию (' + str(self.ServerPort) + ') : ')
        if input_host != '':
            self.ServerHost = input_host
        if input_port != '':
            self.ServerPort = input_port

        # Сохранение настроек
        config.set('ServerInfo', 'HOST', self.ServerHost)
        config.set('ServerInfo', 'PORT', self.ServerPort)
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
        try:
            self.printLog('Подключение к серверу %s:%s...' % (self.ServerHost, str(self.ServerPort)))
            self.cli_sock.connect((self.ServerHost, int(self.ServerPort)))
            self.connected = True
            self.printLog('Подключен.')
        except ConnectionRefusedError:
            self.printLog('Сервер не доступен.')
            self.connected = False
            self.dispose()

    def executeCommandsFromServer(self, commands):
        """Выполнение команд, полученных от сервера"""
        self.printLog("Выполнение команды: %s" % str(commands))
        if len(commands) == 1:
            command = commands[0]
            if command == 'F1':
                self.virtualKeyboard.F1.press()
            if command == 'F2':
                self.virtualKeyboard.F2.press()
            if command == 'F3':
                self.virtualKeyboard.F3.press()
            if command == 'F4':
                self.virtualKeyboard.F4.press()
            if command == 'F5':
                self.virtualKeyboard.F5.press()
            if command == 'F6':
                self.virtualKeyboard.F6.press()
            if command == 'F7':
                self.virtualKeyboard.F7.press()
            if command == 'F8':
                self.virtualKeyboard.F8.press()
            if command == 'F9':
                self.virtualKeyboard.F9.press()
            if command == 'YES':
                time.sleep(0.5)
                self.pressYes()
            if command == 'DanceSong':
                self.danceSong()
            if command == 'Assist':
                self.assist()
            if command == 'Buff':
                self.reBuff()
            if command == 'FollowMe':
                self.followMe()
            if command == 'CoV':
                self.chantOfVictory()
            if command == 'Heal':
                self.self.selfHeal()
        elif len(commands) == 2:
            command = commands[1]
            parameter = commands[0]
            if command == 'F1' and parameter == 'ALT':
                self.printLog("Нажатие кнопки ДА")
                self.pressYes()
            elif command == 'F2' and parameter == 'ALT':
                self.printLog("Использование бафа")
                self.reBuff()
            elif command == 'F3' and parameter == 'ALT':
                self.printLog("Использование Dance Song")
                self.danceSong()
