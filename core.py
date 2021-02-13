import os
import subprocess
import sys
import logging
import time
import is_there_face
import initSetting
import pwd
import AES
import BluetoothServer
import WifiServer
from PyQt5.QtGui import QImage, QPalette, QPixmap, QFont, QPainter, QBrush, QIcon, QColor
from PyQt5.QtCore import Qt, pyqtSlot, QThread
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QGroupBox, QLabel, QVBoxLayout, QHBoxLayout,
                             QPushButton, QDesktopWidget, QLineEdit, QDialog, QPlainTextEdit, QSystemTrayIcon,
                             qApp, QMessageBox)
from threading import Thread

AccessList = [True, False, False, True, True, True]

# AccessList => [CamStatus, BluetoothStatus, WifiStatus, Driver_Keyboard, Driver_Mouse, Driver_USB]
TrayIconState = True
ModelingComplete = False
passwordCorrect = False


class MyApp(QWidget):
    bluetoothTh = Thread(target=BluetoothServer.BluetoothSetting.initBluetoothThread)
    bluetoothTh.start()

    def __init__(self):
        super().__init__()
        self.initUI()

    # noinspection PyTypeChecker
    def initUI(self):
        global TrayIconState
        global ModelingComplete
        global passwordCorrect

        while True:
            if BluetoothServer.programReboot:
                initSetting.Messaging('LSP', '클라이언트의 블루투스 연결이 종료되었습니다.\n프로그램을 리부트합니다.', 'Warning')
            BluetoothServer.isNowLock = False
            passwordCorrect = False
            ModelingComplete = False
            BluetoothServer.programReboot = False
            WifiServer.wifiConnect = False
            result = initSetting.InitSetting()
            res = result.exec()
            if res:
                self.Exit()

            global AccessList
            if initSetting.faceAuth:
                AccessList[0] = True
            if initSetting.bluetoothAuth:
                AccessList[1] = True
            if initSetting.WIFIAuth:
                AccessList[2] = True
            # AccessList[3] = Driver_Keyboard.canRun()
            # AccessList[4] = Driver_Mouse.canRun()
            # AccessList[5] = Driver_USB.canRun()

            palette = QPalette()
            palette.setBrush(QPalette.Background, QColor('Black'))
            self.setPalette(palette)

            if TrayIconState:
                TrayIcon(self)
                TrayIconState = False

            while True:
                count = 0
                BluetoothServer.flag = False

                if not ModelingComplete:
                    push_button4.click()
                    logging.info('Modeling Success!')
                    ModelingComplete = True

                while True:
                    bluetoothThread = Thread(target=BluetoothServer.communication)
                    bluetoothThread.start()
                    bluetoothThread.join()
                    if BluetoothServer.flag:
                        break
                    elif BluetoothServer.programReboot:
                        break

                    push_button3.click()

                    existFace = is_there_face.UserExist
                    percentFace = is_there_face.UserConfidence
                    if not existFace:
                        count += 1
                        print(str(count) + " : " + str(existFace))
                    else:
                        count = 0
                        print(str(count) + " : " + str(existFace) + " >> confidence : " + str(percentFace) + "%")

                    if count == 100:
                        BluetoothServer.isNowLock = True
                        break

                if BluetoothServer.programReboot:
                    TrayIconState = False
                    print(">>>>>>>> Program REBOOT <<<<<<<<")
                    logging.info(">>>>>>>> Program REBOOT <<<<<<<<")
                    break

                mainGroupBox = QGroupBox('Laptop Security Program')
                mainGroupBox.setStyleSheet("Color : white")
                mainGroupBox.setFont(QFont("Arial", 22, weight=QFont.Bold))
                mainGroupBox.setAlignment(Qt.AlignCenter)
                mainVertical = QVBoxLayout()
                grid = QGridLayout()
                grid.addWidget(self.LogViewer(), 1, 0)
                grid.addWidget(self.LiveUserCam(), 0, 0)
                grid.addWidget(self.ProgInfoStatus(AccessList[0], AccessList[1], AccessList[2]), 0, 1)
                grid.addWidget(self.ControlDriverList(AccessList[3], AccessList[4], AccessList[5]), 1, 1)
                mainGroupBox.setLayout(grid)
                mainVertical.addWidget(mainGroupBox)
                # movie = QMovie('image/caution.gif')
                # movie.setSpeed(100)
                # caution = QLabel()
                # caution.setMovie(movie)
                # caution.setAlignment(Qt.AlignCenter)
                # mainVertical.addWidget(caution)
                # movie.start()
                self.setLayout(mainVertical)

                self.introVideo()
                logging.info('IntroVideo End.')
                self.setWindowFlags(Qt.WindowStaysOnTopHint)
                self.activateWindow()
                self.showFullScreen()
                self.raise_()

                if True:
                    logging.info('----------------------------------------')
                    logging.info('- Running Programs List')
                    if AccessList[0]:
                        logging.info('--> Camera Program')
                    if AccessList[1]:
                        logging.info('--> Bluetooth Program')
                    if AccessList[2]:
                        logging.info('--> WIFI Program')
                    logging.info('----------------------------------------')
                    logging.info('- Controlling Driver List')
                    if AccessList[3]:
                        logging.info('--> Keyboard Driver')
                    if AccessList[4]:
                        logging.info('--> Mouse Driver')
                    if AccessList[5]:
                        logging.info('--> USB Driver')
                    logging.info('----------------------------------------')
                    logging.info('Laptop Security Program is Running!!!')

                push_button.click()

                self.close()
                logging.info('===================Unlock=====================')

                if BluetoothServer.programReboot:
                    TrayIconState = False
                    print(">>>>>>>> Program REBOOT <<<<<<<<")
                    logging.info(">>>>>>>> Program REBOOT <<<<<<<<")
                    break

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Q:
            win = Password()
            win.showModal()

        elif e.key() == Qt.Key_W:
            self.Exit()

    def Exit(self):
        self.deleteLater()
        self.close()
        quit()
        exit(1)

    @staticmethod
    def introVideo():
        M = QWidget()
        image_v = ImageViewer()
        # noinspection PyUnresolvedReferences
        vid2.VideoSignal2.connect(image_v.setImage)

        horizontal = QHBoxLayout()
        horizontal.setContentsMargins(0, 0, 0, 0)
        horizontal.addWidget(image_v)

        M.setLayout(horizontal)
        M.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window | Qt.CustomizeWindowHint)
        M.activateWindow()

        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()

        widget = QWidget.geometry(QWidget())
        x = ag.width() - widget.width()
        y = 2 * ag.height() - sg.height() - widget.height()
        M.move(x - 725, y - 240)

        M.show()
        M.raise_()
        push_button2.click()
        M.close()

    @staticmethod
    def LiveUserCam():
        groupbox = QGroupBox('실시간 사용자 화면')
        groupbox.setStyleSheet("Color : white")
        groupbox.setFont(QFont("Arial", 15))

        image_view = ImageViewer()
        if AccessList[0]:
            vid.VideoSignal1.connect(image_view.setImage)

        horizontal = QHBoxLayout()
        if AccessList[0]:
            horizontal.addWidget(image_view)
        groupbox.setLayout(horizontal)
        logging.info('Camera check complete...')

        width = groupbox.width()
        height = groupbox.height()
        groupbox.setAutoFillBackground(True)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap("image/background.jpg").scaled(width + 280, height + 30)))
        groupbox.setPalette(palette)
        return groupbox

    def LogViewer(self):
        groupbox = QGroupBox('Log')
        groupbox.setStyleSheet("Color : white")
        groupbox.setFont(QFont("Arial", 15))

        logTextBox = QPlainTextEditLogger(self)
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().setLevel(logging.DEBUG)
        filename = time.strftime('systemlog/%y%m%d%H%M%S.log')
        fileHandler = logging.FileHandler(filename)
        fileHandler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        logging.getLogger().addHandler(fileHandler)

        layout = QVBoxLayout()
        layout.addWidget(logTextBox.widget)
        logging.info('Logviewer check complete...')

        groupbox.setLayout(layout)

        width = groupbox.width()
        height = groupbox.height()
        groupbox.setFixedWidth(960)
        # groupbox.setFixedHeight(480)
        groupbox.setAutoFillBackground(True)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap("image/background.jpg").scaled(width + 280, height + 30)))
        groupbox.setPalette(palette)
        return groupbox

    @staticmethod
    def ProgInfoStatus(CamStat, BluetoothStat, WifiStat):
        groupbox = QGroupBox('프로그램 정보 및 상태')
        groupbox.setStyleSheet("Color : white")
        groupbox.setFont(QFont("Arial", 15))

        StatusRun = '실행 중'
        StatusClose = '종료 됨'
        CanStatus = QPixmap('image/check.png').scaledToWidth(80).scaledToHeight(80)
        CanNotStatus = QPixmap('image/not.png').scaledToWidth(80).scaledToHeight(80)

        if CamStat:
            CamSt = '카메라 프로그램 ' + StatusRun
        else:
            CamSt = '카메라 프로그램 ' + StatusClose
        logging.info('Camera program check... ok')

        if BluetoothStat:
            BluetoothSt = '블루투스 프로그램 ' + StatusRun
        else:
            BluetoothSt = '블루투스 프로그램 ' + StatusClose
        logging.info('Bluetooth program check... ok')

        if WifiStat:
            WifiSt = '와이파이 프로그램 ' + StatusRun
        else:
            WifiSt = '와이파이 프로그램 ' + StatusClose
        logging.info('WIFI program check... ok')

        horizontal_layout1 = QHBoxLayout()
        horizontal_layout2 = QHBoxLayout()
        horizontal_layout3 = QHBoxLayout()
        horizontal_layout1.setAlignment(Qt.AlignCenter)
        horizontal_layout2.setAlignment(Qt.AlignCenter)
        horizontal_layout3.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        imglb1 = QLabel()
        imglb2 = QLabel()
        imglb3 = QLabel()
        h_layout = [horizontal_layout1, horizontal_layout2, horizontal_layout3]
        imglb = [imglb1, imglb2, imglb3]

        List = [CamSt, BluetoothSt, WifiSt]
        StatusList = [CamStat, BluetoothStat, WifiStat]
        count = 0
        for i in List:
            label = QLabel(i)
            label.setAlignment(Qt.AlignCenter)
            font = label.font()
            font.setPointSize(20)
            font.setItalic(True)
            font.setBold(True)
            label.setFont(font)
            label.setStyleSheet("Color:white;" "background-color:rgba(0, 0, 0, 150);")
            imglb[count].setStyleSheet("background-color:rgba(0, 0, 0, 150);")
            if StatusList[count]:
                imglb[count].setPixmap(CanStatus)
                h_layout[count].addWidget(imglb[count])
            else:
                imglb[count].setPixmap(CanNotStatus)
                h_layout[count].addWidget(imglb[count])
            h_layout[count].addWidget(label)
            layout.addLayout(h_layout[count])
            count += 1

        groupbox.setLayout(layout)
        logging.info('All program load Success!')

        width = groupbox.width()
        height = groupbox.height()
        groupbox.setAutoFillBackground(True)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap("image/background.jpg").scaled(width + 280, height + 30)))
        groupbox.setPalette(palette)
        return groupbox

    @staticmethod
    def ControlDriverList(Dv_Keyboard, Dv_Mouse, Dv_USB):
        groupbox = QGroupBox('제어 중인 드라이버 목록')
        groupbox.setStyleSheet("Color : white")
        groupbox.setFont(QFont("Arial", 15))

        '''
        -> 드라이버 목록들
        -> 아래 'dir' 명령어를 실행하는 이유는 원래 드라이버 서비스 실행하는 부분인데
        -> 테스트 겸해서 아무 명령어로 넣어봄.
        -> cmd 배열에 서비스 목록들 넣어주면 됨.
        '''

        CanControl = '제어 중'
        CanNotControl = '제어 불가'
        CanStatus = QPixmap('image/check.png').scaledToWidth(80).scaledToHeight(80)
        CanNotStatus = QPixmap('image/not.png').scaledToWidth(80).scaledToHeight(80)

        cmd = ['dir']
        os.system('chcp 65001')
        subprocess.Popen(cmd, shell=True)

        if Dv_Keyboard:
            D_Keyboard = '키보드 ' + CanControl
        else:
            D_Keyboard = '키보드 ' + CanNotControl
        logging.info('Keyboard driver check complete...')

        if Dv_Mouse:
            D_Mouse = '마우스 ' + CanControl
        else:
            D_Mouse = '마우스 ' + CanNotControl
        logging.info('Mouse driver check complete...')

        if Dv_USB:
            D_USB = 'USB ' + CanControl
        else:
            D_USB = 'USB ' + CanNotControl
        logging.info('USB driver check complete...')

        horizontal_layout1 = QHBoxLayout()
        horizontal_layout2 = QHBoxLayout()
        horizontal_layout3 = QHBoxLayout()
        horizontal_layout1.setAlignment(Qt.AlignCenter)
        horizontal_layout2.setAlignment(Qt.AlignCenter)
        horizontal_layout3.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout()
        imglb1 = QLabel()
        imglb2 = QLabel()
        imglb3 = QLabel()
        h_layout = [horizontal_layout1, horizontal_layout2, horizontal_layout3]
        imglb = [imglb1, imglb2, imglb3]

        List = [D_Keyboard, D_Mouse, D_USB]
        StatusList = [Dv_Keyboard, Dv_Mouse, Dv_USB]
        count = 0
        for i in List:
            label = QLabel(i)
            label.setAlignment(Qt.AlignCenter)
            font = label.font()
            font.setPointSize(20)
            font.setItalic(True)
            font.setBold(True)
            label.setFont(font)
            label.setStyleSheet("Color : white;" "background-color: rgba(0, 0, 0, 150);")
            imglb[count].setStyleSheet("background-color: rgba(0, 0, 0, 150);")
            if StatusList[count]:
                imglb[count].setPixmap(CanStatus)
                h_layout[count].addWidget(imglb[count])
            else:
                imglb[count].setPixmap(CanNotStatus)
                h_layout[count].addWidget(imglb[count])
            h_layout[count].addWidget(label)
            layout.addLayout(h_layout[count])
            count += 1

        groupbox.setLayout(layout)
        logging.info('All driver control success!')

        width = groupbox.width()
        height = groupbox.height()
        groupbox.setAutoFillBackground(True)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(QPixmap("image/background.jpg").scaled(width + 280, height + 30)))
        groupbox.setPalette(palette)
        return groupbox


class ImageViewer(QWidget):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image = QImage()
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QImage()

    @pyqtSlot(QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")
        self.image = image
        if image.size() != self.size():
            self.setFixedSize(image.size())
        self.update()


class Password(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        Blayout = QHBoxLayout()
        cancel = QPushButton("취소")
        # noinspection PyUnresolvedReferences
        cancel.clicked.connect(self.closeEvent)
        ok = QPushButton("확인")
        # noinspection PyUnresolvedReferences
        ok.clicked.connect(lambda: self.checkPassword(edit.text()))
        Blayout.addWidget(cancel)
        Blayout.addWidget(ok)
        password = QLabel("비밀번호를 입력하세요.")
        edit = QLineEdit()
        edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(password)
        layout.addWidget(edit)
        layout.addLayout(Blayout)
        self.setLayout(layout)
        self.setWindowTitle("Password")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowMinMaxButtonsHint, False)
        self.activateWindow()
        self.raise_()

    def checkPassword(self, text):
        f = open("setting", 'r')
        password = f.read(300)
        f.close()
        if pwd.passwordCheck.passwordHash(text) == AES.aesDecrypt(password):
            global passwordCorrect
            passwordCorrect = True
            self.close()
        else:
            initSetting.Messaging('Error', '비밀번호가 틀렸습니다!', 'Critical')

    def closeEvent(self, e):
        self.reject()

    def showModal(self):
        return super().exec_()


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.widget.setStyleSheet("Color:white;" "background-color:rgba(0, 0, 0, 150);")
        self.widget.verticalScrollBar().setValue(0)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
        self.widget.verticalScrollBar().setValue(self.widget.verticalScrollBar().maximum())


class TrayIcon(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main = parent
        self.trayIcon = QSystemTrayIcon(QIcon('image/icon.png'))
        self.trayIcon.setToolTip('Laptop Security Program v1.0 is Running')
        self.trayIcon.show()
        # noinspection PyUnresolvedReferences
        self.trayIcon.activated.connect(self.on_systray_activated)

    @staticmethod
    def on_systray_activated():
        buttons = qApp.mouseButtons()
        if not buttons:
            msgBox = QMessageBox()
            msgBox.setWindowTitle('Exit')
            msgBox.setText('Are you sure to quit?')
            msgBox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setDefaultButton(QMessageBox.No)
            msgBox.setWindowIcon(QIcon('image/icon.png'))
            msgBox.setWindowFlags(Qt.WindowStaysOnTopHint)
            msgBox.setWindowFlags(msgBox.windowFlags() & ~Qt.WindowCloseButtonHint & ~Qt.WindowMaximizeButtonHint
                                  & ~Qt.WindowMinimizeButtonHint)
            msgBox.activateWindow()
            msgBox.raise_()
            result = msgBox.exec_()

            if result == QMessageBox.Yes:
                WifiServer.EXIT = True
                quit(0)
                sys.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    vid = is_there_face.Face()
    vid2 = is_there_face.ShowVideo()

    push_button = QPushButton()
    push_button2 = QPushButton()
    push_button3 = QPushButton()
    push_button4 = QPushButton()
    # noinspection PyUnresolvedReferences
    push_button.clicked.connect(vid.camera)
    # noinspection PyUnresolvedReferences
    push_button2.clicked.connect(vid2.startVideo)
    # noinspection PyUnresolvedReferences
    push_button3.clicked.connect(vid.scanning)
    # noinspection PyUnresolvedReferences
    push_button4.clicked.connect(vid.modeling)

    ex = MyApp()
    app.exit()
