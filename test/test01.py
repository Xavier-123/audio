# coding:utf-8
# @Author : wangxin
# @Date : 2023/8/9
# @Version : v1


import pathlib
import time

import requests

"""
audio/wave
audio/mpeg
"""


def send_mp3():
    """发送二进制文件"""

    file_name = pathlib.Path(file_path).name
    binary_io = open(file_path, 'rb')

    file_type = 'audio/mpeg'
    # {'file': ("test.pdf", stream, "file/pdf")}
    files = {'file': (file_name, binary_io, file_type)}

    r = requests.post(url, files=files)

    return r.json()


def send_wav():
    """发送二进制文件"""

    file_name = pathlib.Path(file_path).name
    binary_io = open(file_path, 'rb')

    file_type = 'audio/wave'
    # {'file': ("test.pdf", stream, "file/pdf")}
    files = {'file': (file_name, binary_io, file_type)}

    r = requests.post(url, files=files)

    return r.json()


if __name__ == '__main__':
    # url = 'http://192.168.12.84:10000/audio_rec'
    # file_path = "english.wav"
    url = 'http://127.0.0.1:19000/audio_rec'
    # file_path = "zh.wav"
    file_path = "zh.mp3"

    t = time.time()
    res2 = send_wav()
    print(time.time() - t)
    print(res2)
