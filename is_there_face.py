import sys
import os
import numpy as np
import cv2
import core
import logging
import psutil

import initSetting
import BluetoothServer
from PyQt5.QtCore import pyqtSignal, QEventLoop, QTimer, QThread
from PyQt5.QtGui import QImage
from threading import Thread

VideoSave = True
SleepTime = 25    # 적정 수치 : 25, CPU : 31~36%
UserExist = False
UserConfidence = 0
Modeling = cv2.face.LBPHFaceRecognizer_create()


class ShowVideo(QThread):
    camera = cv2.VideoCapture('video/newIntro.mp4')

    ret, image = camera.read()
    if not ret:
        logging.critical('Intro video is not exist!')
        initSetting.Messaging('Error', 'Intro video is not exist!', 'critical')
        sys.exit()
    height, width = image.shape[:2]

    VideoSignal2 = pyqtSignal(QImage)

    # noinspection PyUnresolvedReferences
    def startVideo(self):
        cam = cv2.VideoCapture('video/newIntro.mp4')

        while True:
            ret, image = cam.read()
            if not ret:
                cam.release()
                cv2.waitKey(1)
                cv2.destroyAllWindows()
                break

            color_swap_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            qt_image2 = QImage(color_swap_image.data,
                               self.width,
                               self.height,
                               color_swap_image.strides[0],
                               QImage.Format_RGB888)

            self.VideoSignal2.emit(qt_image2)

            loop = QEventLoop()
            QTimer.singleShot(SleepTime, loop.quit)
            loop.exec_()


class Face(QThread):
    VideoSignal1 = pyqtSignal(QImage)
    ForceEnd = False

    def __init__(self):
        super().__init__()
        self.camera()

    @staticmethod
    def face_detector(img):
        face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        roi = ''

        if faces == ():
            return img, []

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
            roi = img[y:y + h, x:x + w]
            roi = cv2.resize(roi, (200, 200))

        return img, roi

    # noinspection PyUnresolvedReferences,PyBroadException
    def camera(self):
        # print("Execute camera!!")
        global Modeling
        writer = ''

        if VideoSave:
            import time

            cam = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
            ret, image = cam.read()
            height, width = image.shape[:2]

            filename = time.strftime('video/log/%y%m%d%H%M%S')
            fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
            writer = cv2.VideoWriter(filename + '.avi', fourcc, 15, (width, height))

            logging.info('The Blackbox is Ready!')

        # eye_cascade = CascadeClassifier("haarcascade_eye.xml")
        video_capture = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
        capchaFlag = False
        count = 0

        while True:
            bluetoothThread = Thread(target=BluetoothServer.communication)
            bluetoothThread.start()
            bluetoothThread.join()
            if not BluetoothServer.flag:
                break
            elif BluetoothServer.password:
                BluetoothServer.password = False
                result = core.Password()
                result.showModal()
                if core.passwordCorrect:
                    break
            elif BluetoothServer.programReboot:
                break

            ret, frame = video_capture.read()
            height, width = frame.shape[:2]

            if not ret:
                logging.critical('Camera functions cannot be performed.')
                Messaging('Error', '카메라 기능을 수행할 수 없습니다!', 'Critical')
            else:
                MainFrame = cv2.flip(frame, 1)
                image, userFace = self.face_detector(MainFrame)

                if VideoSave:
                    if count < 10:
                        writer.write(image)
                        count += 1
                    else:
                        logging.info('Video Saving...')
                        writer.write(image)
                        count = 0

                if len(userFace) != 0:
                    try:
                        userFace = cv2.cvtColor(userFace, cv2.COLOR_BGR2GRAY)
                        result = Modeling.predict(userFace)

                        if result[1] < 500:
                            confidence = int(100 * (1 - (result[1]) / 300))
                            display_string = str(confidence) + '% Confidence it is user'

                            if confidence > 75:
                                logging.info(display_string + " >> Check Admin!")
                                capchaFlag = True
                            else:
                                logging.info(display_string + " >> It's not administrator!")
                    except:
                        logging.info('Modeling Error!')
                        pass

                if not capchaFlag:
                    color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    qt_image1 = QImage(color_swapped_image.data,
                                       width,
                                       height,
                                       color_swapped_image.strides[0],
                                       QImage.Format_RGB888)
                    self.VideoSignal1.emit(qt_image1)

                    cpu = psutil.cpu_percent()
                    global SleepTime
                    if cpu >= 70:       # cpu 사용량이 70% 이상이면 SleepTime을 늘려 cpu 사용량을 자동으로 줄임. (성능저하)
                        SleepTime = SleepTime + 5
                    elif cpu <= 20:     # cpu 시용량이 20% 이하이면 SleepTime을 줄여 cpu 사용량을 자동으로 늘림. (성능증가)
                        SleepTime = SleepTime - 5
                    else:
                        if 30 <= cpu <= 60:     # cpu 사용량이 정상 수치면 SleepTime을 원래대로 되돌리려 함.
                            if SleepTime > 25:
                                SleepTime = SleepTime - 5
                            else:
                                SleepTime = SleepTime + 5

                    loop = QEventLoop()
                    QTimer.singleShot(SleepTime, loop.quit)
                    loop.exec_()
                else:
                    return True

    # noinspection PyBroadException
    def scanning(self):
        global UserExist
        global Modeling
        UserExist = False

        video_capture = cv2.VideoCapture(0 + cv2.CAP_DSHOW)

        ret, frame = video_capture.read()

        if not ret:
            initSetting.Messaging('Error', '카메라 기능을 실행할 수 없습니다!', 'Critical')
        else:
            # MainFrame = cv2.flip(frame, 1)
            image, userFace = self.face_detector(frame)
            global UserConfidence

            try:
                userFace = cv2.cvtColor(userFace, cv2.COLOR_BGR2GRAY)
                result = Modeling.predict(userFace)
                confidence = 0
                if result[1] < 500:
                    confidence = int(100 * (1 - (result[1]) / 300))
                if confidence > 75:
                    UserExist = True
                    UserConfidence = confidence
                else:
                    UserExist = False
            except Exception:
                pass

    @staticmethod
    def modeling():
        data_path = 'image/user/'
        onlyfiles = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
        Training_Data, Labels = [], []

        for i, files in enumerate(onlyfiles):
            image_path = data_path + onlyfiles[i]
            images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            Training_Data.append(np.asarray(images, dtype=np.uint8))
            Labels.append(i)

        Labels = np.asarray(Labels, dtype=np.int32)

        global Modeling
        Modeling.train(np.asarray(Training_Data), np.asarray(Labels))
