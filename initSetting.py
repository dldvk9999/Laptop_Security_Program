import sys
import os
import time
from threading import Thread

import pwd
import Facial_Recognition_Part1
import Facial_Recognition_Part2
import BluetoothServer
import WifiServer
import AES

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QDesktopWidget, QPushButton, QLabel, QGroupBox, \
    QHBoxLayout, QDialog, QMessageBox, QCheckBox, QApplication, QLineEdit, QProgressBar

SavedFace = False
TrainFace = False

faceAuth = False
bluetoothAuth = True
WIFIAuth = False

saveModelName = False
ModelName = ''
closeSignal = False


class StatChange:
    @staticmethod
    def saveName(st, name):
        global saveModelName
        if st.isChecked():
            saveModelName = True
            global ModelName
            ModelName = name
        else:
            saveModelName = False

    @staticmethod
    def stateChangeWIFI(st):
        global WIFIAuth
        if st == 2:
            WIFIAuth = True
        else:
            WIFIAuth = False


def ImagingAndTrainning():
    global SavedFace
    SavedFace = False
    SavedFace = Facial_Recognition_Part1.Main()


def Messaging(title, text, icon):
    msgBox = QMessageBox()
    msgBox.setWindowTitle(title)
    msgBox.setText(text)
    msgBox.setStandardButtons(QMessageBox.Yes)
    if icon == 'Information':
        msgBox.setIcon(QMessageBox.Information)
    elif icon == 'Question':
        msgBox.setIcon(QMessageBox.Question)
    elif icon == 'Warning':
        msgBox.setIcon(QMessageBox.Warning)
    else:
        msgBox.setIcon(QMessageBox.Critical)
    msgBox.setDefaultButton(QMessageBox.Yes)
    msgBox.setWindowIcon(QIcon('image/information-icon.png'))
    msgBox.setWindowFlags(Qt.WindowStaysOnTopHint)
    msgBox.setWindowFlags(msgBox.windowFlags() & ~Qt.WindowCloseButtonHint & ~Qt.WindowMaximizeButtonHint
                          & ~Qt.WindowMinimizeButtonHint)
    msgBox.activateWindow()
    msgBox.raise_()
    result = msgBox.exec_()
    return result


class InitSetting(QDialog):
    bluetoothConnection = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        global faceAuth
        global bluetoothAuth
        global WIFIAuth
        global SavedFace
        global TrainFace
        faceAuth = True
        bluetoothAuth = False
        WIFIAuth = False
        SavedFace = False
        TrainFace = False

        self.initUI()

    def initUI(self):
        tabs = QTabWidget()

        tabs.addTab(self.FaceSetting(), "Face")
        tabs.addTab(self.BluetoothSetting(), "Bluetooth")
        tabs.addTab(self.WIFISetting(), "WIFI")
        tabs.addTab(self.passwordSave(), "Password")
        tabs.addTab(self.Developers(), "Developers")

        close_button = QPushButton('닫기')
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(self.CloseButton)
        execute_button = QPushButton('실행')
        # noinspection PyUnresolvedReferences
        execute_button.clicked.connect(self.next)

        button_layout = QHBoxLayout()
        button_layout.addWidget(close_button)
        button_layout.addWidget(execute_button)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(tabs)
        mainLayout.addLayout(button_layout)

        self.setLayout(mainLayout)
        self.setWindowTitle('설정')
        self.setWindowIcon(QIcon('image/setting.png'))
        self.resize(400, 200)
        self.center()
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

    def closeEvent(self, event):
        if SavedFace is None or True:
            if TrainFace:
                self.close()
            else:
                self.CloseButton()
        else:
            Messaging('Error', '사용자 얼굴 저장이 되지 않았습니다. \n\"사용자 얼굴 저장\" 버튼을 눌러 저장해주십시오.', 'Critical')

    def next(self, event):
        global TrainFace
        global bluetoothAuth
        TrainFace = Facial_Recognition_Part2.Main()

        if not bluetoothAuth:
            Messaging('Error', '블루투스 연동을 완료해주세요!', 'Information')
        elif not pwd.passwordStatus:
            Messaging('Error', '비밀번호 저장을 완료해주세요!', 'Information')
        else:
            self.closeEvent(event)

    # noinspection PyAttributeOutsideInit
    def CloseButton(self):
        if BluetoothServer.devices != '':
            sys.exit(0)

        global closeSignal
        closeSignal = True

        self.closeDialog = QDialog()
        closeLayout = QHBoxLayout()
        self.progress = QProgressBar()

        closeLayout.addWidget(self.progress)
        self.closeDialog.setLayout(closeLayout)
        self.closeDialog.setWindowTitle("프로세스 정리 중...")
        self.closeDialog.setWindowFlags(
            self.closeDialog.windowFlags() & ~Qt.WindowCloseButtonHint & ~Qt.WindowContextHelpButtonHint)

        th = Thread(target=self.progressValue)
        th.start()
        self.closeDialog.exec()
        th.join()

        sys.exit(0)

    def progressValue(self):
        count = 0
        if BluetoothServer.devices == '':
            while True:
                count += 1
                time.sleep(0.05)
                self.progress.setValue(count)
                if count == 100:
                    break
        elif WifiServer.wifiConnect:
            while True:
                count += 50
                time.sleep(1)
                self.progress.setValue(count)
                if count == 100:
                    break
        self.closeDialog.reject()

    @staticmethod
    def FaceSetting():
        MainGroupbox = QWidget()
        layout = QVBoxLayout()
        groupbox = QGroupBox()
        groupbox.setFlat(True)
        mainLayout = QVBoxLayout()
        MainFrame = QWidget()

        F_layout = QVBoxLayout()
        FaceSaveBtn = QPushButton("사용자 얼굴 저장")
        # noinspection PyUnresolvedReferences
        FaceSaveBtn.clicked.connect(ImagingAndTrainning)
        label1 = QLabel("※ 클릭 시 100장의 사용자 얼굴을 인식하여 저장합니다.")
        F_layout.addWidget(label1)
        F_layout.addWidget(FaceSaveBtn)
        MainFrame.setLayout(F_layout)

        mainLayout.addWidget(MainFrame)
        groupbox.setLayout(mainLayout)
        label2 = QLabel("얼굴 인식을 이용한 잠금해제는 기본적으로 실행됩니다.")
        layout.addWidget(label2)
        layout.addWidget(groupbox)
        MainGroupbox.setLayout(layout)

        return MainGroupbox

    # noinspection PyUnresolvedReferences
    def BluetoothSetting(self):
        MainGroupbox = QWidget()
        layout = QVBoxLayout()
        groupbox = QGroupBox()
        groupbox.setFlat(True)

        B_layout = QVBoxLayout()
        BB_layout = QHBoxLayout()
        howto = QLabel("※ 아래에 블루투스로 통신할 휴대폰의 이름(모델명)을 적어주세요.")
        userBluetoothName = QLineEdit()
        saveCheck = QCheckBox("저장하기")
        saveCheck.stateChanged.connect(lambda: StatChange.saveName(saveCheck, userBluetoothName.text()))

        if os.path.isfile("USERNAME"):
            # noinspection PyBroadException
            try:
                f = open("USERNAME", 'r')
                data = f.read(300)
                f.close()
                data = AES.aesDecrypt(data)
                userBluetoothName.setText(data)
                saveCheck.setText("저장 됨")
                saveCheck.setChecked(True)
                saveCheck.setEnabled(False)
            except Exception:
                Messaging('LSP', 'USERNAME 파일이 깨졌습니다.\n다시 생성해주십시오.', 'Information')
                os.remove("USERNAME")

        BluetoothSaveBtn = QPushButton("블루투스 연동")
        Btn_layout = QHBoxLayout()
        Btn_layout.setContentsMargins(0, 0, 0, 0)
        Btn_layout.addWidget(BluetoothSaveBtn)

        if not saveCheck.isEnabled():
            deleteFile = QPushButton("모델명 삭제")
            Btn_layout.addWidget(deleteFile)
            deleteFile.clicked.connect(lambda: self.deleteModelFile(saveCheck, Btn_layout, 'USERNAME'))

        Btn_widget = QWidget()
        Btn_widget.setLayout(Btn_layout)
        BluetoothSaveBtn.clicked.connect(
            lambda: BluetoothServer.BluetoothSetting(Btn_widget, saveCheck, userBluetoothName.text()))
        B_layout.addWidget(howto)
        BB_layout.addWidget(userBluetoothName)
        BB_layout.addWidget(saveCheck)
        B_layout.addLayout(BB_layout)
        B_layout.addWidget(Btn_widget)

        groupbox.setLayout(B_layout)
        label1 = QLabel("블루투스는 원격으로 잠금/해제를 하기 위해 사용됩니다.")
        layout.addWidget(label1)
        layout.addWidget(groupbox)
        MainGroupbox.setLayout(layout)
        return MainGroupbox

    @staticmethod
    def WIFISetting():
        MainGroupbox = QWidget()
        layout = QVBoxLayout()
        groupbox = QGroupBox()
        groupbox.setFlat(True)
        check = QCheckBox("사용하기")
        # noinspection PyUnresolvedReferences
        check.stateChanged.connect(StatChange.stateChangeWIFI)
        mainLayout = QVBoxLayout()
        MainFrame = QWidget()

        W_layout = QVBoxLayout()
        WifiSaveBtn = QPushButton("와이파이 연계")
        # noinspection PyUnresolvedReferences
        WifiSaveBtn.clicked.connect(lambda: WifiServer.Socket(WifiSaveBtn))
        W_layout.addWidget(WifiSaveBtn)
        MainFrame.setLayout(W_layout)

        mainLayout.addWidget(MainFrame)
        groupbox.setLayout(mainLayout)
        label1 = QLabel("도난감지를 설정하려면 아래를 체크해주세요.")
        layout.addWidget(label1)
        layout.addWidget(check)
        layout.addWidget(groupbox)
        MainGroupbox.setLayout(layout)
        return MainGroupbox

    # noinspection PyUnresolvedReferences
    def passwordSave(self):
        MainFrame = QWidget()
        MainLayout = QVBoxLayout()
        MainLayout.setAlignment(Qt.AlignCenter)

        SubLayout = QVBoxLayout()
        label_save = QLabel('>> 비밀번호가 저장되어 있습니다.')

        delBtn = QPushButton("삭제")

        SubLayout.addWidget(label_save)
        SubLayout.addWidget(delBtn)

        label = QLabel("비밀번호를 입력해주세요.")
        edit = QLineEdit()
        edit.setEchoMode(QLineEdit.Password)

        label2 = QLabel("비밀번호 확인")
        edit2 = QLineEdit()
        edit2.setEchoMode(QLineEdit.Password)

        Btn = QPushButton("저장")
        # noinspection PyUnresolvedReferences
        Btn.clicked.connect(lambda: pwd.passwordCheck.SameCheck(edit.text(), edit2.text()))

        SubLayout.addWidget(label)
        SubLayout.addWidget(edit)
        SubLayout.addWidget(label2)
        SubLayout.addWidget(edit2)
        SubLayout.addWidget(Btn)

        delBtn.clicked.connect(lambda: self.deleteFile(label, label2, edit, edit2, Btn, label_save, delBtn, 'setting'))

        if os.path.isfile('setting'):
            label.setVisible(False)
            label2.setVisible(False)
            edit.setVisible(False)
            edit2.setVisible(False)
            Btn.setVisible(False)
        else:
            label_save.setVisible(False)
            delBtn.setVisible(False)

        MainLayout.addLayout(SubLayout)

        MainFrame.setLayout(MainLayout)
        return MainFrame

    @staticmethod
    def Developers():
        MainFrame = QWidget()
        MainLayout = QVBoxLayout()
        MainLayout.setAlignment(Qt.AlignCenter)

        programName = QLabel("::Laptop Security Program Developers::")
        MainFont = programName.font()
        MainFont.setBold(True)
        MainFont.setPointSize(15)
        programName.setFont(MainFont)
        Mentor = QLabel("Mentor\t: 김지현 - General supervision")
        Mentee1 = QLabel("Mentee\t: 최지원(Team Leader) - User recognition  module Dev.")
        Mentee2 = QLabel("Mentee\t: 곽현석 - Device filter driver Dev.")
        Mentee3 = QLabel("Mentee\t: 박종근 - Main GUI & core Dev.")
        Other = QLabel("Other\t: 최근영 - Sub Dev and help others.")

        MainLayout.addWidget(programName)
        MainLayout.addWidget(Mentor)
        MainLayout.addWidget(Mentee1)
        MainLayout.addWidget(Mentee2)
        MainLayout.addWidget(Mentee3)
        MainLayout.addWidget(Other)

        MainFrame.setLayout(MainLayout)
        return MainFrame

    def deleteFile(self, label, label2, edit, edit2, Btn, label_save, delBtn, filename):
        reply = QMessageBox.information(self, 'LSP', '저장된 비밀번호를 삭제하시겠습니까?',
                                        QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # noinspection PyBroadException
            try:
                os.remove(filename)
                Messaging('LSP', '삭제되었습니다.', 'Information')
                label.setVisible(True)
                label2.setVisible(True)
                edit.setVisible(True)
                edit2.setVisible(True)
                Btn.setVisible(True)
                label_save.setVisible(False)
                delBtn.setVisible(False)
                pwd.passwordStatus = False
            except Exception:
                pass

        return label, label2, edit, edit2, Btn, label_save, delBtn

    def deleteModelFile(self, saveCheck, Btn_layout, filename):
        reply = QMessageBox.information(self, 'LSP', '저장된 모델명을 삭제하시겠습니까?',
                                        QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # noinspection PyBroadException
            try:
                os.remove(filename)
                Messaging('LSP', '삭제되었습니다.', 'Information')
                saveCheck.setEnabled(True)
                saveCheck.setText("저장하기")
                saveCheck.setChecked(True)
                Btn_layout.itemAt(1).widget().deleteLater()
            except Exception:
                pass
        return saveCheck, Btn_layout


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InitSetting()
    sys.exit(app.exec_())
