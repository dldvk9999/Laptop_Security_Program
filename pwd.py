import initSetting

import hashlib
import os
import re
import AES

from PyQt5.QtWidgets import QWidget

passwordStatus = False
if os.path.isfile('setting'):
    passwordStatus = True


class passwordCheck(QWidget):
    @staticmethod
    def SameCheck(first, second):
        if first != second:
            initSetting.Messaging('Password', '비밀번호가 다릅니다!', 'Warning')
        else:
            passwordCheck.passwordSecurity(first)

    @staticmethod
    def passwordSecurity(pw):
        if 0 < len(pw) < 10:
            initSetting.Messaging('Password', '비밀번호의 길이가 10보다 작습니다!', 'Warning')
        elif len(pw) == 0:
            initSetting.Messaging('Password', '비밀번호를 입력해주세요.', 'Warning')
        elif not re.search(r'\d', pw):
            initSetting.Messaging('Password', '숫자가 없습니다.', 'Warning')
        elif not re.search(r'[a-z]', pw):
            initSetting.Messaging('Password', '문자가 없습니다.', 'Warning')
        elif not re.search(r"[~!@#$%^&*]", pw):
            initSetting.Messaging('Password', '특수문자가 없습니다.', 'Warning')
        else:
            passwordCheck.Save(pw)

    @staticmethod
    def Save(text):
        text = passwordCheck.passwordHash(text)
        txt = AES.aesEncrypt(text)
        f = open("setting", 'w')
        f.write(txt)
        f.close()
        initSetting.Messaging('Password', '비밀번호 저장 완료!', 'Information')
        global passwordStatus
        passwordStatus = True

    @staticmethod
    def passwordHash(txt):
        enc = hashlib.md5()
        enc.update(txt.encode('utf-8'))
        hashString = enc.hexdigest()
        return hashString
