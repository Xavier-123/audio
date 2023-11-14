# coding:utf-8
# @Author : wangxin
# @Date : 2023/8/14
# @Version : v1
import os.path
import pathlib
import uuid
import shutil

from conf.config import cache_dir
from main.error_define import AudioTypeError, VideoTypeError, FileTypeError


def type_check(file_type: str):
    """检验文件类型"""

    if not file_type:
        raise AudioTypeError("音频类型缺失")
    else:
        file_type = file_type.lower()

    if file_type == "audio/wave" or file_type == "audio/wav":
        suffix = ".wav"
    elif file_type == "audio/mpeg" or "audio/mp3":
        suffix = ".mp3"
    else:
        raise AudioTypeError("当前仅支持wav、mp3文件")

    return suffix


def tmp_file(suffix, filename, user_id) -> pathlib.Path:
    file_name = filename if filename else f"{uuid.uuid4().hex}.{suffix}"
    file_path = pathlib.Path(cache_dir, str(user_id))

    if not os.path.exists(file_path):
        os.mkdir(str(file_path))
    else:
        shutil.rmtree(str(file_path) + "/")
        os.makedirs(file_path)
    file_path = pathlib.Path(str(file_path), file_name)

    return file_path


def type_check_video(file_type: str):
    """检验文件类型"""
    if not file_type:
        raise VideoTypeError("视频类型缺失")
    else:
        file_type = file_type.lower()

    if file_type == "video/mp4":
        suffix = ".mp4"
    elif file_type == "video/x-msvideo":
        suffix = ".avi"
    else:
        raise VideoTypeError("当前仅支持avi、mp4文件")

    return suffix


def type_check_file(file_type: str):
    """检验文件类型"""
    if not file_type:
        raise FileTypeError("文本类型缺失")
    else:
        file_type = file_type.lower()

    if file_type == "application/pdf":
        suffix = ".pdf"
    elif file_type == "text/plain":
        suffix = ".txt"
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        suffix = ".docx"
    elif file_type == "application/rtf":
        suffix = ".rtf"
    else:
        raise VideoTypeError("当前仅支持pdf、txt、docx、rtf")

    return suffix


def check_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path