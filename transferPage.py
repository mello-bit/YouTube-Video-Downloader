import signal
import sys
from os.path import join
from os import chdir

from datamanager import Manager
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
import http.server
# provides access to the BSD socket interface
import socket
# a framework for network servers
import socketserver
# to display a Web-based documents to users
import webbrowser
# to generate qrcode
import pyqrcode
from pyqrcode import QRCode

import png  # for converting into png format
import os

from datamanager import Manager, Profile
from threading import Thread



class TransferWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(join('uis', 'transfer.ui'), self)
        self.stopButton.clicked.connect(self.close)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.mouseMoveEvent = self.moveWindow
        self.startServer()

    def closeEvent(self, event) -> None:
        print('closeEvent fired!')
        Thread(target=self.closeServer, daemon=True).start()
        # socket.close()
        # self.closeServer()
    
    def _startServer(self):
        directory = Manager.getActiveUser().settings['directories']['home']
        # в directory уже лежит директория пользователя. Используй её
        # ..Здесь открой сервер..
        PORT = 8010
        user_path = os.path.join(os.getcwd(), directory)
        chdir(user_path)

        Handler = http.server.SimpleHTTPRequestHandler

        hostname = socket.gethostname()

        # finding the IP address of the PC
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = "http://" + s.getsockname()[0] + ":" + str(PORT)
        link = IP

        # converts the IP address into a Qrcode
        url = pyqrcode.create(link)
        # saves the Qrcode inform of svg
        url.png("myqr.png", scale=8)
        # opens the Qrcode image in the web browser
        # webbrowser.open('myqr.png')

        qrImage = "myqr.png"  # Сюда положи путь к qr коду.
        self.qrLabel.setFixedSize(450, 450)
        self.qrLabel.setScaledContents(True)
        self.qrLabel.setPixmap(QPixmap(qrImage))
        os.remove("myqr.png")
        # Creating the HTTP request and serving the
        # folder in the PORT 8010,and the pyqrcode is generated
        self.server = socketserver.TCPServer(("", PORT), Handler)
        # continuous stream of data between client and server
        with self.server as httpd:
            try:
                print("serving at port", PORT)
                print("Type this in your Browser", IP)
                print("or Use the QRCode")
                # httpd.serve_forever(poll_interval=1)
                
                Thread(target=httpd.serve_forever(), daemon=True).start()
                assassin = Thread(target=self.server.shutdown)
                assassin.daemon = True
                assassin.start()
                # когда появится ui я это добавлю на кнопку
                # if input() == "a":
                #     exit(0)
                # print('httpd server has been successfully stopped')
            except KeyboardInterrupt:
                httpd.socket.close()

        #........................
        # qrImage = "myqr.png"  # Сюда положи путь к qr коду.
        # self.qrLabel.setFixedSize(450, 450)
        # self.qrLabel.setScaledContents(True)
        # self.qrLabel.setPixmap(QPixmap(os.path.join(user_path, qrImage)))
        # print(os.path.join(user_path, qrImage))

    def startServer(self):
        Thread(
            target=self._startServer, daemon=True
        ).start()
    
    def closeServer(self):
        # Функция выполниться при закрытии окна (Нажатии на кнопку)
        # ..Здесь закрой сервер..
        # PORT = 8010
        # server = socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler)
        if getattr(self, 'server', None) is not None and getattr(self, "closing", None):
            self.closing = True
            assassin = Thread(target=self.server.shutdown)
            assassin.daemon = True
            assassin.start()
            chdir('../')  # Will still break the program, if the user will open and close the ui fast enough !TODO!
        #........................

    def moveWindow(self, event) -> None:
        self.move(self.pos() + event.globalPos() - self.clickPosition)
        self.clickPosition = event.globalPos()
        event.accept()

    def mousePressEvent(self, event) -> None:
        self.clickPosition = event.globalPos()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.instance().login = 'N1qro'

    window = TransferWindow()
    window.show()
    app.exec_()