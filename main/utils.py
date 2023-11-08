import os
import pathlib
import shutil

from starlette.datastructures import UploadFile
from pydub import AudioSegment
from pydub.utils import make_chunks
from conf.config import cache_dir, slice_dir
import PyPDF2


# 获取已上传视频
def get_video_lists():
    video_lists = os.listdir(cache_dir)
    video_lists = [i for i in video_lists if ".mp4" in i or ".avi" in i]
    return video_lists

# 获取缓存音频
def get_audio_lists():
    audio_lists = os.listdir(cache_dir)
    audio_lists = [i for i in audio_lists if ".mp3" in i or ".wav" in i]
    return audio_lists


def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    duration = audio.duration_seconds
    return duration


def clear_slice_file(path):
    folder_path = path
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        os.makedirs(folder_path)
    else:
        os.mkdir(folder_path)


def slice_audio(file, user_id):
    print(type(file))
    if isinstance(file, pathlib.WindowsPath):
        audio = AudioSegment.from_file(file)
    elif isinstance(file, UploadFile):
        name = file.filename
        audio = AudioSegment.from_file(cache_dir + f"/{user_id}/" + name, "mp3")
    else:
        name = file.name
        audio = AudioSegment.from_file(cache_dir + f"/{user_id}/" + name, "mp3")

    size = 50000  # 切割的毫秒数 50s=50000
    chunks = make_chunks(audio, size)  # 将文件切割为50s一个
    # clear_slice_file(slice_dir)
    slice_dir = cache_dir + f"/{user_id}/save"
    clear_slice_file(slice_dir)
    for i, chunk in enumerate(chunks):
        chunk_name = slice_dir + "/{0}.wav".format(i)
        chunk.export(chunk_name, format="wav")
    return slice_dir

def file2word(path):
    suffix = str(path).split(".")[-1]
    if suffix == "pdf":
        return pdf2word(path)
    if suffix == "docx":
        return
    if suffix == "txt":
        with open(path, 'r') as f:
            lines = f.readlines()
        return ''.join(lines)

def pdf2word(path):
    with open(path, 'rb') as file:
        all_text = ""
        reader = PyPDF2.PdfReader(file)
        for page in range(len(reader.pages)):
            page_obj = reader.pages[page]
            text = page_obj.extract_text()
            all_text += text
    all_text = filter_word(all_text)
    return all_text

def filter_word(words):
    words = words.replace("", "").replace("", "").replace(" ", "").replace("→", "").replace("↑", "").replace(
        "↓", "").replace("•", "").replace("--", "-").replace("▉", "").replace("★", "")
    return words