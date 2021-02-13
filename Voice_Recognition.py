from sys import byteorder
from array import array
from struct import pack

import pyaudio
import wave
import os
import logging
import speech_recognition as sr
from PyQt5.QtCore import QThread

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100
UNLOCK_VOICE_FLAG = False


class VoiceRecognization(QThread):
    def __init__(self):
        super().__init__()
        self.record_to_file('command.wav')

        r = sr.Recognizer()
        audio = sr.AudioFile("command.wav")

        with audio as source:
            command = r.record(source)

        text = r.recognize_google(audio_data=command, language="ko-KR")

        if text == '잠금 해제':
            global UNLOCK_VOICE_FLAG
            UNLOCK_VOICE_FLAG = True
            logging.info(">>> VOICE UNLOCK <<<")
        else:
            logging.info("Didn't say 'unlock'.")

        os.remove("command.wav")

    @staticmethod
    def is_silent(snd_data):
        return max(snd_data) < THRESHOLD

    @staticmethod
    def normalize(snd_data):
        MAXIMUM = 16384
        times = float(MAXIMUM) / max(abs(i) for i in snd_data)

        result = array('h')
        for i in snd_data:
            result.append(int(i * times))
        return result

    @staticmethod
    def trim(snd_data):
        def _trim(data=snd_data):
            snd_started = False
            result = array('h')

            for i in data:
                if not snd_started and abs(i) > THRESHOLD:
                    snd_started = True
                    result.append(i)

                elif snd_started:
                    result.append(i)
            return result

        # Trim to the left
        snd_data = _trim(snd_data)

        # Trim to the right
        snd_data.reverse()
        snd_data = _trim(snd_data)
        snd_data.reverse()
        return snd_data

    @staticmethod
    def add_silence(snd_data, seconds):
        result = array('h', [i for i in range(0, int(seconds * RATE))])
        result.extend(snd_data)
        result.extend([i for i in range(0, int(seconds * RATE))])
        return result

    def record(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=1, rate=RATE,
                        input=True, output=True,
                        frames_per_buffer=CHUNK_SIZE)

        num_silent = 0
        snd_started = False

        result = array('h')

        while 1:
            # little endian, signed short
            snd_data = array('h', stream.read(CHUNK_SIZE))
            if byteorder == 'big':
                snd_data.byteswap()
            result.extend(snd_data)

            silent = self.is_silent(snd_data)

            if silent and snd_started:
                num_silent += 1
            elif not silent and not snd_started:
                snd_started = True

            if snd_started and num_silent > 30:
                break

        sample_width = p.get_sample_size(FORMAT)
        stream.stop_stream()
        stream.close()
        p.terminate()

        result2 = self.normalize(result)
        result2 = self.trim(result2)
        result2 = self.add_silence(result2, 0.5)
        return sample_width, result2

    def record_to_file(self, path):
        sample_width, data = self.record()
        data = pack('<' + ('h' * len(data)), *data)

        wf = wave.open(path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(RATE)
        wf.writeframes(data)
        wf.close()
