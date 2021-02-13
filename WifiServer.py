import socket
import time
import initSetting

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QPushButton
from threading import Thread

wc_sock = ''
ws_sock = ''
wifiConnect = False
EXIT = False
server_sock = socket.socket(socket.AF_INET)


class Socket(QWidget):
    def __init__(self, WifiSaveBtn):
        super().__init__()
        self.setting = QDialog()
        self.setting.setWindowTitle("LSP")
        self.setting.setWindowIcon(QIcon('image/icon.png'))
        self.setting.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setting.setWindowFlags(
            self.setting.windowFlags() & ~Qt.WindowCloseButtonHint & ~Qt.WindowMaximizeButtonHint
            & ~Qt.WindowMinimizeButtonHint)
        self.label = QLabel("LSP 모바일 - 메뉴 - Wifi Setting에서 다음 IP로 접속해주세요.\n")
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.label)

        host = socket.gethostbyname(socket.gethostname())
        self.label1 = QLabel(host)
        self.label1.setAlignment(Qt.AlignCenter)
        self.label1.setStyleSheet("font: bold 20px; margin: 10px;")
        mainLayout.addWidget(self.label1)

        cancelBtn = QPushButton("취소")
        # noinspection PyUnresolvedReferences
        cancelBtn.clicked.connect(self.closeEXEC)
        mainLayout.addWidget(cancelBtn)
        self.setting.setLayout(mainLayout)
        self.setting.activateWindow()

        self.SocketStart(host, WifiSaveBtn)

    def closeEXEC(self):
        server_sock.close()
        self.setting.reject()

    def SocketStart(self, host, WifiSaveBtn):
        th = Thread(target=self.connect, args=(host, WifiSaveBtn))
        th.start()
        self.setting.exec()

    def connect(self, host, WifiSaveBtn):
        port = 9999

        global server_sock
        server_sock = socket.socket(socket.AF_INET)
        # noinspection PyBroadException
        try:
            server_sock.bind((host, port))
        except Exception:
            initSetting.Messaging("LSP", "각 소켓 주소(프로토콜/네트워크 주소/포트)는 하나만 사용할 수 있습니다", "Warning")
            return

        server_sock.listen(1)

        print("기다리는 중")
        # noinspection PyBroadException
        try:
            client_sock, addr = server_sock.accept()
        except Exception:
            print("사용자에 의해 소켓 통신 연동 중지")
            return
        self.label1.setVisible(False)
        self.label.setText("연결 성공!")
        time.sleep(0.008)
        self.setting.resize(self.label.sizeHint())
        time.sleep(3)
        self.setting.reject()

        global wc_sock
        wc_sock = client_sock

        print('Connected by', addr)

        data = client_sock.recv(1024)
        print(data.decode("utf-8"))

        WifiSaveBtn.setEnabled(False)
        global wifiConnect
        wifiConnect = True

        th = Thread(target=Communication)
        th.start()
        th.join()

        return WifiSaveBtn


class Communication(QThread):
    def __init__(self):
        super().__init__()
        self.SendSignal()

    @staticmethod
    def SendSignal():
        global wc_sock
        global server_sock
        global EXIT
        client_sock = wc_sock

        while True:
            data2 = 1
            if initSetting.closeSignal:
                break
            # noinspection PyBroadException
            try:
                if EXIT:
                    break
                # noinspection PyUnresolvedReferences
                client_sock.send(data2.to_bytes(1, byteorder='little'))
                print("signal 전송")
                time.sleep(2)
            except Exception:
                global wifiConnect
                wifiConnect = False
                print("메시지 전송 오류 : 스마트폰에서 소켓통신이 끊긴 것 같습니다. LSP_APP을 확인하여주시기 바랍니다.")
                break

        return
