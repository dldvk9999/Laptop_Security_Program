#!/usr/bin/env python3
import time

import bluetooth
import logging

import AES
import initSetting
import Voice_Recognition
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QDesktopWidget, QDialog, QWidget, QVBoxLayout, QLabel, QPushButton
from threading import Thread

c_sock = ''
s_sock = ''
closeSignal = False
flag = False
programReboot = False
password = False
isNowLock = False
successBluetooth = False
portSet = 0
devices = ''


class BluetoothSetting(QWidget):
    bluetoothConnection = pyqtSignal(str)

    # noinspection PyUnresolvedReferences
    def __init__(self, Btn_widget, saveCheck, addr):
        super().__init__()
        if addr == '' or addr is None:
            initSetting.Messaging('LSP', '휴대폰에 모델명을 입력해주세요!', 'Information')
            return
        else:
            self.Listing(Btn_widget, saveCheck, addr)

    def Show(self):
        self.exec()

    def Close(self):
        self.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

    @staticmethod
    def initBluetoothThread():
        nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True,
                                                    flush_cache=True, lookup_class=False)
        global devices
        devices = nearby_devices

    def threadWork(self, deviceName, label, cancelButton):
        global c_sock
        global s_sock
        global closeSignal
        global devices
        text = "Collecting Bluetooth list stored in PC..."
        print(text)
        logging.info(text)

        if devices == '' or devices is None:
            import core
            core.MyApp.bluetoothTh.join()

        nearby_devices = devices
        print("Collecting Success.")
        logging.info("Collecting Success.")
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("", bluetooth.PORT_ANY))
        if closeSignal:
            closeSignal = False
            server_sock.close()
            print(">>> User canceled.")
            logging.info(">>> User canceled.")
            self.msg.reject()
            return
        server_sock.listen(1)

        port = server_sock.getsockname()[1]

        global portSet
        if portSet == 0:
            portSet = port

        if port != portSet:
            text = "The RFCOMM number has been increased.\n" + \
                   "This LSP program uses only one RFCOMM number and does not allow multiple Bluetooth connections.\n" + \
                   "This is a problem that occurs because the previous Bluetooth socket is not normally terminated.\n" + \
                   "Restart the LSP program (if it is still in the task manager after termination, restart after forced termination),\n" + \
                   "and run LSP_Controller again after complete termination. The LSP program is automatically closed after 10sec."
            label.setText('RFCOMM 번호가 증가하였습니다.\n' +
                          '본 LSP 프로그램은 RFCOMM 번호 하나만을 사용하며 다중 블루투스 연결은 허용하지 않습니다.\n' +
                          '이는 이전 블루투스 소켓이 정상적으로 종료되지 않아 발생하는 문제로 ' +
                          'LSP 프로그램을 재시작해주시고(종료 후 작업관리자에 아직 남아있다면 강제종료 후 재시작),\n' +
                          'LSP_Controller 또한 완전 종료 후 다시 실행해주시기 바랍니다.\n' +
                          'LSP 프로그램은 10초 후 자동 종료됩니다.')
            print(text)
            logging.info(text)
            time.sleep(10)
            self.msg.reject()
            sys.exit(-123456789)

        uuid = "00000000-1111-2222-3333-444444444444"

        bluetooth.advertise_service(server_sock, "SampleServer", service_id=uuid,
                                    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                    profiles=[bluetooth.SERIAL_PORT_PROFILE], )

        text = "Waiting for connection on RFCOMM channel " + str(port) + " ..."
        label.setText("이제 LSP_Controller 어플을 통해 블루투스 연결을 해주십시오.\n" +
                      "※ 이 작업은 취소할 수 없습니다!")
        cancelButton.setEnabled(False)
        cancelButton.setVisible(False)
        time.sleep(0.01)
        self.msg.resize(label.sizeHint())

        print(text)
        logging.info(text)

        client_sock, client_info = server_sock.accept()

        addrList = []
        nameList = []

        count = 0
        for addr, name in nearby_devices:
            if addr and name:
                try:
                    addrList.append(addr)
                    nameList.append(name)
                except UnicodeEncodeError:
                    addrList.append(addr)
                    nameList.append(name.encode("utf-8", "replace"))

            count += 1

        for i in range(0, count):
            if deviceName == nameList[i]:
                # noinspection PyUnresolvedReferences
                self.bluetoothConnection.emit(addrList[i])
                global successBluetooth
                successBluetooth = True

                if initSetting.saveModelName:
                    modelname = initSetting.ModelName
                    modelname = AES.aesEncrypt(modelname)
                    f = open("USERNAME", 'w')
                    f.write(modelname)
                    f.close()

                c_sock = client_sock
                s_sock = server_sock
                initSetting.bluetoothAuth = True

                text = "Accepted connection from " + addrList[i] + "\nWelcome " + nameList[i] + " !"
                label.setText(addrList[i] + ' 주소 연결 성공!\n' + nameList[i] + '님 환영합니다!')
                time.sleep(0.008)
                self.msg.resize(label.sizeHint())
                print(text)
                logging.info(text)
                time.sleep(3)
                self.msg.reject()
                return

        label.setText('일치하는 모델명이 없습니다!\n' +
                      '사용 전에 먼저 PC와 기연결을 하고 실행해주시거나 모델명을 확인해주시기 바랍니다.')
        time.sleep(5)
        text = "There is no matching model name. Bluetooth Disconnected."
        print(text)
        logging.info(text)
        self.msg.reject()

        client_sock.close()
        server_sock.close()
        initSetting.bluetoothAuth = False

    def Listing(self, Btn_widget, saveCheck, deviceName):
        # noinspection PyAttributeOutsideInit
        self.msg = QDialog()
        label = QLabel('PC에 저장된 블루투스 목록을 불러옵니다.\n' +
                       '잠시 기다려 주십시오...\n' +
                       '※ 프로그램이 \'응답없음\'이라고 떠도 기다려 주세요.')
        cancelButton = QPushButton('취소')
        # noinspection PyUnresolvedReferences
        cancelButton.clicked.connect(lambda: self.closeEXEC(cancelButton, label))
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(label)
        mainLayout.addWidget(cancelButton)
        self.msg.setLayout(mainLayout)
        self.msg.setWindowTitle("LSP")
        self.msg.setWindowIcon(QIcon('image/icon.png'))
        self.msg.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.msg.setWindowFlags(self.msg.windowFlags() & ~Qt.WindowCloseButtonHint & ~Qt.WindowMaximizeButtonHint
                                & ~Qt.WindowMinimizeButtonHint)
        self.msg.activateWindow()
        th = Thread(target=self.threadWork, args=(deviceName, label, cancelButton), daemon=True)
        th.start()
        self.msg.exec()
        th.join()

        global successBluetooth
        if successBluetooth:
            Btn_widget.setEnabled(False)
            saveCheck.setEnabled(False)

        return Btn_widget, saveCheck

    @staticmethod
    def closeEXEC(cancelButton, label):
        global closeSignal
        closeSignal = True
        cancelButton.setEnabled(False)
        label.setText("블루투스를 종료 중입니다. 잠시만 기다려주세요...")


class communication(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.SendCommand()

    @staticmethod
    def SendCommand():
        global c_sock
        global s_sock
        client_sock = c_sock
        server_sock = s_sock
        # noinspection PyBroadException
        try:
            client_sock.settimeout(0.01)
        except Exception:
            pass

        try:
            global flag
            global isNowLock
            data = b''

            # noinspection PyBroadException
            try:
                data = client_sock.recv(1024)
            except Exception:
                data = ' '
            finally:
                if not data == b'\x00' and not data == b'':
                    # noinspection PyBroadException
                    try:
                        data = data.decode('utf-8')
                        data = AES.aesDecrypt(data)
                    except Exception:
                        data = ' '
                elif data == b'':
                    global programReboot
                    programReboot = True
                    client_sock.close()
                    server_sock.close()
                    initSetting.bluetoothAuth = False
                    return
                else:
                    data = ' '

            if data == 'lock':
                flag = True
                isNowLock = True

            elif data == 'unlock':
                flag = False

            elif data == 'Voice Recognition':
                if isNowLock:
                    print("please speak a Word into the microphone")
                    logging.info("please speak a Word into the microphone")
                    # noinspection PyBroadException
                    try:
                        Voice_Recognition.VoiceRecognization()
                    except Exception:
                        data = 'No human voice was recorded.'
                    if Voice_Recognition.UNLOCK_VOICE_FLAG:
                        flag = False
                else:
                    data = 'The screen is not locked at this time.'

            elif data == 'Password Recognition':
                if isNowLock:
                    global password
                    password = True
                else:
                    data = 'The screen is not locked at this time.'

            if not data == ' ':
                print("Received >>", data)
                logging.info("Received >> " + data)
        except OSError:
            pass
