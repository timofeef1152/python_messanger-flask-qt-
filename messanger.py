import sys
import threading
import time
from datetime import datetime

import requests
from PyQt5 import QtWidgets

from clientui import Ui_MainWindow


class MessangerApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.button_clicked)
        self.mutex = threading.Lock()  # locker
        threading.Thread(target=self.update_messages).start()  # создание потока

    def send_message(self, username, password, text):
        response = requests.post(
            'http://127.0.0.1:5000/auth',
            json={'username': username, 'password': password}
        )
        if response.json()['ok']:
            response = requests.post(
                'http://127.0.0.1:5000/send',
                json={'username': username, 'password': password, 'text': text}
            )
        else:
            self.add_to_chat('Аутентификация не пройдена')
            return False
        if not response.json()['ok']:
            self.add_to_chat('Сообщение не отправлено')
            return False
        return True

    def button_clicked(self):
        try:
            if self.send_message(
                    self.plainTextEdit.toPlainText(),
                    self.plainTextEdit_2.toPlainText(),
                    self.textEdit.toPlainText()
            ):
                self.textEdit.setText('')
        except:
            self.add_to_chat('Произошла ошибка при отправке сообщения')

    def update_messages(self):
        last_time = 0
        server_online = True

        while True:
            try:
                response = requests.get(
                    'http://127.0.0.1:5000/messages',
                    params={'after': last_time}
                )
                messages = response.json()['messages']
                for message in messages:
                    beauty_time = datetime.fromtimestamp(message['time'])
                    beauty_time = beauty_time.strftime("%Y.%m.%d %H:%M:%S")
                    self.add_to_chat(f"{message['username']} {beauty_time}\n{message['text']}")
                    last_time = message['time']

                server_online = True
                time.sleep(0.1)
            except:
                if server_online:
                    self.add_to_chat('Произошла ошибка при получении сообщений')
                server_online = False

    def add_to_chat(self, text):
        self.mutex.acquire()
        self.textBrowser.append(f'{text}\n')
        self.scroll_chat_to_bottom()
        # self.textBrowser.repaint()
        # pass # TODO
        self.mutex.release()

    def scroll_chat_to_bottom(self):
        self.textBrowser.verticalScrollBar().setValue(
            self.textBrowser.verticalScrollBar().maximum())


app = QtWidgets.QApplication([])
window = MessangerApp()
window.show()

sys.exit(app.exec())
