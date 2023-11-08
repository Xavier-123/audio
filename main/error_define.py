# coding:utf-8
# @Author : wangxin
# @Date : 2022/1/10
# @Version : v1


class CustomError(Exception):
    """自定义错误类型"""

    def __init__(self, message=""):
        super().__init__()
        self.message = message
        self.code = -1

    def __str__(self):
        return self.message


class AudioTypeError(CustomError):
    """声音类型错误"""

    def __init__(self, message=""):
        super().__init__()
        self.message = f"Audio type error! {message}"
        self.code = 1


class VideoTypeError(CustomError):
    """视频类型错误"""

    def __init__(self, message=""):
        super().__init__()
        self.message = f"Video type error! {message}"
        self.code = 4

class FileTypeError(CustomError):
    """文件类型错误"""

    def __init__(self, message=""):
        super().__init__()
        self.message = f"File type error! {message}"
        self.code = 5


class BinaryDecodingError(CustomError):
    """二进制文件解码错误"""

    def __init__(self, message=""):
        super().__init__()
        self.message = f"Binary decoding error! {message}"
        self.code = 2


class SpeechRecognitionError(CustomError):
    """语音识别错误"""

    def __init__(self, message=""):
        super().__init__()
        self.message = f"Speech recognition error! {message}"
        self.code = 3
