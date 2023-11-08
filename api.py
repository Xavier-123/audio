# coding:utf-8
# @Author : wangxin
# @Date : 2023/8/9
# @Version : v1

import zipfile
import time
import uvicorn
import pathlib
from fastapi import FastAPI, UploadFile, File, Form, status
from fastapi.responses import JSONResponse, FileResponse
from flask import Flask, request
from paddlespeech.cli.asr import ASRExecutor
from paddlespeech.cli.text import TextExecutor
from pydantic import BaseModel, Field
from pydub import AudioSegment
from moviepy.video.io.VideoFileClip import VideoFileClip
import glob
import pyttsx3
import uuid
import requests
import sys
import os
import img2pdf
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
import urllib.parse

system = sys.platform

from conf.config import use_cache, cache_dir, large_model_ip, large_model_port, large_model_name
from main.check_tool import type_check, tmp_file, type_check_video, type_check_file
from main.error_define import BinaryDecodingError, CustomError
from main.log import logger
from main.utils import get_video_lists, clear_slice_file, get_audio_duration, slice_audio, file2word

# 语音识别
asr = ASRExecutor()
# 标点恢复
text_punc = TextExecutor()
# 模型最大输入长度
maximum_sequence_length = 511

app = FastAPI(title="语音识别", version="v1.0", )


class RequestModel(BaseModel):
    text: str = Field("会议纪要格式", example="今天的天气真不错啊你下午有空吗我想约你一起去吃饭")


class ResponseModel(BaseModel):
    isSuc: bool = Field(True, example=True)
    code: int = Field(0, example=0)
    msg: str = Field("Succeed", example="Succeed~")
    res: dict = Field({}, example={})


def audio2text(file_path, user_id):
    # 判断文件时长
    file_time = get_audio_duration(file_path)
    path = pathlib.Path(file_path)
    if float(file_time) >= 50:
        slice_dir = slice_audio(path, user_id)
        text = ""
        files = glob.glob(slice_dir + "/*")

        if "win" in system:
            files = sorted(files, key=lambda x: int(x.split("\\")[-1].split(".")[0]))
        else:
            files = sorted(files, key=lambda x: int(x.split("/")[-1].split(".")[0]))

        for file in files:
            # 语音识别
            # print(file)
            _res = asr.__call__(file, force_yes=True)
            text += _res
        logger.info(text)

        # 每次输出最大值为513
        text_len = len(text)
        res = ""
        for i in range(0, text_len, maximum_sequence_length):
            if maximum_sequence_length > text_len - i:
                slice_text = text[i:]
            else:
                slice_text = text[i: i + maximum_sequence_length]
            res += text_punc.__call__(text=slice_text)
        logger.info(res)
    else:
        text = asr.__call__(path, force_yes=True)
        if not use_cache:
            path.unlink(missing_ok=True)
        logger.info(text)
        res = text_punc.__call__(text=text)
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"isSuc": True, "code": 0, "msg": "Success ~", "res": res})


@app.post(path='/asr', summary="bytes", response_model=ResponseModel, tags=["语音识别"])
async def interface(
        file: UploadFile,
        user_id: int = Form(default=1, description="用户ID", example=1)
):
    logger.info(file.content_type)

    # 文件类型校验
    suffix = type_check(file.content_type)
    # 生成文件名: pathlib.Path对象
    file_path = tmp_file(suffix, file.filename, user_id)

    # 将文件保存在本地
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise BinaryDecodingError(e)

    # 判断文件时长
    file_time = get_audio_duration(file_path)
    if float(file_time) >= 50:
        slice_dir = slice_audio(file, user_id)
        res = ""
        files = glob.glob(slice_dir + "/*")
        print("files:", files)

        if "win" in system:
            files = sorted(files, key=lambda x: int(x.split("\\")[-1].split(".")[0]))
        else:
            files = sorted(files, key=lambda x: int(x.split("/")[-1].split(".")[0]))

        for file in files:
            # 语音识别
            _res = asr.__call__(file, force_yes=True)
            res += _res
    else:
        # 语音识别
        res = asr.__call__(file_path, force_yes=True)
        if not use_cache:
            file_path.unlink(missing_ok=True)

    content = {"isSuc": True, "code": 0, "msg": "Success ~", "res": res}
    logger.info(content)
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@app.post(path='/punc', summary="bytes", response_model=ResponseModel, tags=["标点恢复"])
async def interface(req: RequestModel):
    text = req.text

    logger.info(text)

    # 每次输出最大值为513
    text_len = len(text)
    res = ""
    for i in range(0, text_len, maximum_sequence_length):
        if maximum_sequence_length > text_len - i:
            slice_text = text[i:]
        else:
            slice_text = text[i: i + maximum_sequence_length]
        print(len(slice_text))
        res += text_punc.__call__(text=slice_text)
    content = {"isSuc": True, "code": 0, "msg": "Success ~", "res": res}
    # logger.info(content)
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@app.post(path='/asr_punc', summary="bytes", response_model=ResponseModel, tags=["语音识别+标点恢复"])
async def interface(
        file: UploadFile,
        user_id: int = Form(default=1, description="用户ID", example=1)
):
    logger.info(file.content_type)

    # 文件类型校验
    suffix = type_check(file.content_type)
    # 生成文件名: pathlib.Path对象
    file_path = tmp_file(suffix, file.filename, user_id)

    # 将文件保存在本地
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise BinaryDecodingError(e)

    try:
        return audio2text(file_path, user_id)
    except Exception as e:
        raise "audio to text is error."


# 调用大模型润色
@app.post(path='/polish', response_model=ResponseModel, tags=["语句润色"])
async def large_model_polish(req: RequestModel):
    conv_uid = uuid.uuid1()
    conv_uid = "599fd1de-6c95-11ee-b598-0242ac11000a"
    # print(uuid.uuid1())

    url = f"http://{large_model_ip}:{large_model_port}/api/v1/chat/completions"
    prompt = f"你是一位专业的会议记录员,请从专业角度润色并总结这下面这句话 ”{req.text}“,要简介专业。返回格式：会议内容：xxx。"
    data = {
        "chat_mode": "chat_normal",
        "conv_uid": conv_uid,
        "model_name": large_model_name,
        "user_input": prompt
    }
    # print(prompt)
    inquire_post_response = requests.post(url, json=data)
    res = inquire_post_response.content.decode('utf-8').split("\ndata:")[-1]

    '''后续新增删除会话功能'''
    pass

    return {"isSuc": True, "code": 0, "msg": "Success ~", "res": {"res": res}}


@app.post(path='/uploadVideo_And_toAudio', response_model=ResponseModel, tags=["上传视频, 视频转音频，音频转文字"])
async def uploadVideo_And_toAudio(
        file: UploadFile = File(description="MP4和AVI格式的视频文件"),
        to_word: bool = Form(default=True, description="是否转为文字", example="True"),
        start_time: int = Form(default=0, description="截取开始时间", example=0),
        end_time: int = Form(default=0, description="截取结束时间", example=0),
        user_id: int = Form(default=1, description="用户ID", example=1)
):
    uid = uuid.uuid1()
    logger.info(file.content_type)

    # 文件类型校验
    suffix = type_check_video(file.content_type)
    # 生成文件名: pathlib.Path对象
    file_path = tmp_file(suffix, file.filename, user_id)
    name = str(file.filename).split(".")[0] + f"_{start_time}_{end_time}.mp3"

    # 将文件保存在本地
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        # res = f"{name} is exits."
    except Exception as e:
        raise BinaryDecodingError(e)

    # 视频转音频
    try:
        video_path = pathlib.Path(cache_dir + f'/{user_id}/', file.filename)
        video = AudioSegment.from_file(video_path)

        # 视频流截取
        if start_time == 0 and end_time == 0:
            video = video
        elif start_time >= 0 and end_time >= start_time and end_time <= video.duration_seconds:
            start_time = start_time * 1000
            end_time = end_time * 1000
            video = video[start_time: end_time]
        else:
            raise "start time or end time is error."

        save_path = pathlib.Path(cache_dir + f'/{user_id}/', name)
        video.export(out_f=save_path, format="mp3")
    except Exception as e:
        raise {"isSuc": True, "code": -1, "msg": "fail ~", "res": {"res": "video to audio is fail"}}

    # 音频转文字
    if to_word:
        try:
            return audio2text(save_path, user_id)
        except Exception as e:
            raise "audio to text is error."
    return {"isSuc": True, "code": 0, "msg": "Success ~",
            "res": {"res": f"file is upload success, save in {save_path}"}}


@app.post(path='/slice_video', tags=["截取视频"])
async def slice_video(
        file: UploadFile = File(description="MP4和AVI格式的视频文件"),
        start_time_min: int = Form(default=0, description="截取开始时间", example=0),
        start_time_second: int = Form(default=0, description="截取开始时间", example=0),
        end_time_min: int = Form(default=0, description="截取结束时间", example=0),
        end_time_second: int = Form(default=0, description="截取结束时间", example=0),
        user_id: int = Form(default=1, description="用户ID", example=1)
):
    try:
        slice_file_path = cache_dir + f"/{user_id}"
        if not os.path.exists(slice_file_path):
            os.makedirs(slice_file_path)
        slice_file_path = slice_file_path + "/download/"
        clear_slice_file(slice_file_path)
        name = file.filename.split(".")[0]
        # 将文件保存在本地
        try:
            path = slice_file_path + file.filename
            content = await file.read()
            with open(path, "wb") as f:
                f.write(content)
        except Exception as e:
            raise BinaryDecodingError(e)

        start_time = (0, start_time_min, start_time_second)
        end_time = (0, end_time_min, end_time_second)
        start_time_s = start_time[0] * 3600 + start_time[1] * 60 + start_time[2]
        stop_time_s = end_time[0] * 3600 + end_time[1] * 60 + end_time[2]
        source_video = VideoFileClip(path)
        if start_time_min == start_time_min == 0 and end_time_min == end_time_second == 0:
            video = source_video  # 执行剪切操作
        else:
            video = source_video.subclip(int(start_time_s), int(stop_time_s))  # 执行剪切操作
        save_path = slice_file_path + f"{name}_{start_time_min}_{start_time_second}_{end_time_min}_{end_time_second}.mp4"
        video.write_videofile(save_path)  # 输出文件
        video.close()

    except Exception as e:
        raise {"isSuc": False, "code": -1, "msg": "fail ~", "res": {"res": "video to audio is fail"}}
    return FileResponse(save_path, media_type="video/mp4")


# @app.post(path='/text2audio', tags=["文字转语音"])
# async def text2audio(
#         text: str = Form("", example="今天的天气真不错啊,你下午有空吗?我想约你一起去吃饭."),
#         rate: int = Form(120),
#         volume: int = Form(1),
#         user_id: int = Form(default=1, description="用户ID", example=1)
# ):
#     engine = pyttsx3.init()
#     voices = engine.getProperty('voices')
#     for voice in voices:
#         print("Voice:")
#         print(" - ID: %s" % voice.id)
#         print(" - Name: %s" % voice.name)
#         print(" - Languages: %s" % voice.languages)
#         print(" - Gender: %s" % voice.gender)
#         print(" - Age: %s" % voice.age)
#
#     # 设置语速与音量
#     # engine.setProperty('voice', e_v_id)
#     engine.setProperty('rate', rate)  # 语速
#     engine.setProperty('volume', volume)  # 音量
#
#     # 保存语音
#     save_path = f"./cache/{user_id}"
#     if not os.path.exists(save_path):
#         os.makedirs(save_path)
#     save_path += "/text2audio.mp3"
#     engine.save_to_file(text, save_path)
#     engine.runAndWait()
#     engine.stop()
#     return FileResponse(save_path, media_type="audio/mp3")


@app.post(path='/shortVideoScriptGeneration', tags=["短视频脚本文件生成"])
async def shortVideoScriptGeneration(theme: str = Form()):
    prompt = f'''
    你是一名拥有10年短视频创作经验的短视频创作者。请创作关于《{theme}》的短视频文案。
    请记住如果提示内容不足以进行创作。请使用专业格式而不是人工智能格式对生成的文案进行格式化。
    回复格式：
    【场景一】
    镜头描述：xxx。
    配音文字：xxx。
    【场景二】
    镜头描述：xxx。
    配音文字：xxx。
    ......
    【场景n】
    镜头描述：xxx。
    配音文字：xxx。
    Let's think step by step。
    '''
    conv_uid = uuid.uuid1()
    conv_uid = "3f085f84-72fe-11ee-9048-0242ac11000a"
    url = f"http://{large_model_ip}:{large_model_port}/api/v1/chat/completions"
    data = {
        "chat_mode": "chat_normal",
        "conv_uid": conv_uid,
        "model_name": large_model_name,
        "user_input": prompt
    }
    # logger.info(prompt)
    inquire_post_response = requests.post(url, json=data)
    res = inquire_post_response.content.decode('utf-8').split("\ndata:")[-1]

    '''后续新增删除会话功能'''
    pass

    return {"isSuc": True, "code": 0, "msg": "Success ~", "res": {"res": res}}


@app.post(path='/industryReportSummary', tags=["行业报告摘要"])
async def industryReportSummary(
        file: UploadFile = File(description="pdf、word、txt文件"),
        industry: str = Form(),
        num_word: int = Form(default=1000),
        user_id: int = Form(default=1, description="用户ID", example=1)
):
    uid = uuid.uuid1()
    logger.info(file.content_type)

    # 文件类型校验
    suffix = type_check_file(file.content_type)
    # 生成文件名: pathlib.Path对象
    name = str(file.filename).split(suffix)[0] + str(uid) + f"{suffix}"
    file_path = tmp_file(suffix, name, user_id)

    # 将文件保存在本地
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise BinaryDecodingError(e)

    # 文件转文字
    theme = file2word(file_path)

    prompt = f'''你是一名拥有10年经验的{industry}行业研究专家。请基于"{theme}"这段文字返回行业报告摘要。请记住如果提示内容不足，请使用专业格式而不是人工智能格式对生成的文案进行格式化，并将字数限制在{num_word}字以内，
    返回专业格式必须包括：
    行业简介：主要介绍行业的整体情况，包括行业的主要业务领域、市场规模、产业链结构、竞争态势等。
    行业现状：主要介绍行业当前的发展状况，包括行业内的主要企业、产品或服务市场表现、行业发展的主要趋势等。
    市场特征：主要分析行业市场的特征，包括市场的主要参与者、市场份额分布、市场发展潜力等。
    企业特征：主要分析行业内企业的特征，包括企业的规模、产品或服务的特色、企业的竞争力等。
    发展环境：主要分析行业发展的环境，包括政策环境、经济环境、技术环境等对行业发展的影响等。
    发展趋势：主要预测行业发展的趋势，包括市场规模的预期、技术发展的趋势、政策法规的影响等。
    Let's think step by step。
    '''

    conv_uid = uuid.uuid1()
    conv_uid = "3f085f84-72fe-11ee-9048-0242ac11000a"
    url = f"http://{large_model_ip}:{large_model_port}/api/v1/chat/completions"
    data = {
        "chat_mode": "chat_normal",
        "conv_uid": conv_uid,
        "model_name": large_model_name,
        "user_input": prompt
    }
    logger.info(prompt)
    inquire_post_response = requests.post(url, json=data)
    res = inquire_post_response.content.decode('utf-8').split("\ndata:")[-1]
    logger.info(res)

    '''后续新增删除会话功能'''
    pass

    return {"isSuc": True, "code": 0, "msg": "Success ~", "res": {"res": res}}


@app.post(path='/scrapy_by_keyword', tags=["关键字搜索"])
async def scrapy_by_url(
        keyword: str = Form()
):
    options = Options()
    options.add_argument('--no-sandbox')  # 亲测 Debian 必须加，Ubuntu 随意
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')

    dicts = {}
    url_pre = f"https://www.iresearch.com.cn/search?type=1&keyword="
    url = url_pre + urllib.parse.quote(keyword)
    request = requests.get(url)
    pre_url = "https://www.iresearch.com.cn"
    if 'iresearch.com.cn/search' in url:
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(2)
        data = driver.page_source
        driver.close()

        # 创建响应对象
        res = HtmlResponse(url=url, body=data, encoding='utf-8', request=request)
        print(res)

        url_back = res.xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]//a/@href").getall()
        urls = [pre_url + i for i in url_back]
        names = res.xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]//a/img/@alt").getall()

        ids_url = [0, 2, 4, 6, 8, 10, 12, 14, 16]
        for i, val in enumerate(zip(ids_url, names)):
            dicts[urls[val[0]]] = val[1]

    return {"isSuc": True, "code": 0, "msg": "Success ~", "res": {"res": dicts}}


@app.post(path='/scrapy_by_url', tags=["行业报告生成"])
async def scrapy_by_url(
        url: str = Form(),
        user_id: int = Form(default=1, description="用户ID", example=1)
):
    id = url.split("id=")[1].split("&")[0]
    t1 = time.time()

    path = f"./cache/{user_id}"
    if not os.path.exists(path):
        os.makedirs(path)
    path = path + "/pacong/"
    clear_slice_file(path)
    for i in range(1, 100):
        img = f'https://pic.iresearch.cn/rimgs/{id}/{i}.jpg'
        response = requests.get(img)
        if response.status_code == 200:
            file2 = open(path + f"{id}_{i}.jpg", "wb")
            file2.write(response.content)
            file2.close()
        else:
            break

    t2 = time.time()
    imgs = []
    for fname in os.listdir(path):
        img_path = os.path.join(path, fname)
        imgs.append(img_path)
    t3 = time.time()
    imgs.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))


    file = open(path + "test.pdf", "wb")
    file.write(img2pdf.convert(imgs))
    file.close()
    t4 = time.time()
    print(t2 - t1, t3 - t2, t4 - t3)

    return FileResponse(path + "test.pdf", media_type="application/pdf")


@app.post(path='/weekly_report_writing', tags=["周报生成"])
async def scrapy_by_url(
        text: str = Form()
):
    prompt = f'''你是一位职场周报总结小助理。请根据"{text}"这段文本，结合本周工作概要，进行分点概括和扩写，写出周报，风格为简洁专业。'''
    # Let's think step by step。

    conv_uid = uuid.uuid1()
    conv_uid = "3f085f84-72fe-11ee-9048-0242ac11000a"
    url = f"http://{large_model_ip}:{large_model_port}/api/v1/chat/completions"
    data = {
        "chat_mode": "chat_normal",
        "conv_uid": conv_uid,
        "model_name": large_model_name,
        "user_input": prompt
    }
    logger.info(prompt)
    inquire_post_response = requests.post(url, json=data)
    res = inquire_post_response.content.decode('utf-8').split("\ndata:")[-1]
    logger.info(res)

    '''后续新增删除会话功能'''
    pass

    return {"isSuc": True, "code": 0, "msg": "Success ~", "res": {"res": res}}


# 自定义错误
@app.exception_handler(CustomError)
async def unexcept_exception_handler(_, exc: CustomError):
    content = {"isSuc": False, "code": exc.code, "msg": str(exc), "res": {}}
    logger.error(f"{content}")

    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


# 意料之外的错误
@app.exception_handler(Exception)
async def unexcept_exception_handler(_, exc: Exception):
    content = {"isSuc": False, "code": -1, "msg": str(exc), "res": {}}

    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=18510)
