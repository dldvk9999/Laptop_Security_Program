# -*- coding: utf-8 -*-
import hashlib
import base64
import re
from Crypto.Cipher import AES
from PyQt5.QtCore import QThread

BLOCK_SIZE = 16
privateKey2 = '738475CE202BCBA5EF11CF409C1ED7AD'  # '힘내 항상 난 NULL 응원해' -> MD5 해시 값
privateKey1 = '69af60e2fc6f580f3250eb0f7efb9612'  # 'LSP Controller Application' -> MD5 해시 값


class AESCryptoCBC(QThread):
    def __init__(self, key):
        # Initial vector를 0으로 초기화하여 16바이트 할당함
        super().__init__()
        iv = chr(0) * 16
        # aes cbc 생성
        self.crypto = AES.new(key, AES.MODE_CBC, iv.encode('utf-8'))

    def encrypt(self, data):
        enc = self.crypto.encrypt(data)
        return enc

    def decrypt(self, enc):
        dec = self.crypto.decrypt(enc)
        return dec


def aesDecrypt(CipherMessage):
    CipherMessage = base64.b64decode(CipherMessage)
    initAes = AESCryptoCBC(bytes(privateKey1.encode('utf-8')))
    message = initAes.decrypt(bytes(CipherMessage)).decode('utf-8')
    msg, time = message.split("_")

    aes = AESCryptoCBC(bytes(privateKey2.encode('utf-8')))
    data = base64.b64decode(time)
    time = aes.decrypt(bytes(data)).decode('utf-8')
    time = re.sub("[^0-9]*", "", time)

    hashString = privateKey2 + time
    enc = hashlib.md5()
    enc.update(hashString.encode('utf-8'))
    KEY = enc.hexdigest()

    aes2 = AESCryptoCBC(bytes(KEY.encode('utf-8')))
    data = base64.b64decode(msg)
    # noinspection PyBroadException
    try:
        dec = aes2.decrypt(bytes(data)).decode('utf-8')
    except Exception:
        dec = "Failed to decrypt."
    dec = re.sub("[^a-zA-Z0-9가-힣ㄱ-ㅎㅏ-ㅣ. ]*", "", dec)

    return dec.strip()


def aesEncrypt(PlainMessage):
    import time
    timeSet = str(int(time.time() * 1000.0))

    concat = privateKey2 + timeSet
    hashString = hashlib.md5()
    hashString.update(concat.encode('utf-8'))
    KEY = hashString.hexdigest()

    pad = lambda s: s + (16 - len(s) % 16) * b' ' if type(s) is bytes else s + (16 - len(s) % 16) * ' '
    raw = pad(PlainMessage)
    aes = AESCryptoCBC(KEY.encode('utf-8'))
    enc = base64.b64encode(aes.encrypt(raw.encode('utf-8')))

    raw2 = pad(timeSet)
    aes2 = AESCryptoCBC(privateKey2.encode('utf-8'))
    enc2 = base64.b64encode(aes2.encrypt(raw2.encode('utf-8')))

    finalEnc = enc + b"_" + enc2
    raw3 = pad(finalEnc)
    finalAES = AESCryptoCBC(privateKey1.encode('utf-8'))
    cipherMessage = base64.b64encode(finalAES.encrypt(raw3))

    return cipherMessage.decode('utf-8')
