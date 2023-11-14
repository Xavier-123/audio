# '''方式一、pyttsx3'''
# import pyttsx3
# engine = pyttsx3.init()
# text = "可以看到ZH-CN的参数，表示的是中文，然后将代码修改成如下即可"
# # 设置语速与音量
# # engine.setProperty('voice', e_v_id)
# engine.setProperty('rate', 1000)    # 语速
# engine.setProperty('volume', 1)     # 音量
# engine.say(text)
#
# # 保存语音
# engine.save_to_file(text, "./asd.mp3")
#
# engine.runAndWait()
# # pyttsx3.speak("可以看到ZH-CN的参数，表示的是中文，然后将代码修改成如下即可")


# '''方式二、大模型'''
# from transformers import AutoProcessor, AutoModel
#
# processor = AutoProcessor.from_pretrained("F:/inspur/AUDIO_MODEL/bark-small")
# model = AutoModel.from_pretrained("F:/inspur/AUDIO_MODEL/bark-small")
# # processor.to("cuda:0")
# model.to("cuda:0")
#
# # text_prompt = """WOMAN: I would like an oatmilk latte please.MAN: Wow, that's expensive!"""
# text_prompt = "你好, 我叫周杰伦。嗯~。哈哈很高兴认识大家。"
#
# inputs = processor(
#     # text=["Hello, my name is Suno. And, uh — and I like pizza. [laughs] But I also have other interests such as playing tic tac toe."],
#     text=[text_prompt],
#     return_tensors="pt",
# )
# inputs.to("cuda:0")
#
# speech_values = model.generate(**inputs, do_sample=True)
# print(speech_values)
#
# from IPython.display import Audio
# sampling_rate = model.generation_config.sample_rate
# Audio(speech_values.cpu().numpy().squeeze(), rate=sampling_rate)
#
# import scipy
# # sampling_rate = model.config.sample_rate
# sampling_rate = model.generation_config.sample_rate
# scipy.io.wavfile.write("bark_out2.wav", rate=sampling_rate, data=speech_values.cpu().numpy().squeeze())


import uvicorn
from fastapi import Form, FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
import urllib.parse
import requests
import time

app = FastAPI(title="语音识别", version="v1.0", )


# 爬虫 www.iresearch.com.cn通过关键字范围搜索
@app.post(path='/scrapy_by_keyword')
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

        # /html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[1]
        url_back = res.xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]//a/@href").getall()
        urls = [pre_url + i for i in url_back]

        # /html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[2]/div[1]/a/img/@alt
        names = res.xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]//a/img/@alt").getall()

        ids_url = [0, 2, 4, 6, 8, 10, 12, 14, 16]
        for i, val in enumerate(zip(ids_url, names)):
            dicts[urls[val[0]]] = val[1]

    return {"isSuc": True, "code": 0, "msg": "Success ~", "res": {"res": dicts}}


def pdf2word(path):
    import PyPDF2

    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in range(len(reader.pages)):
            page_obj = reader.pages[page]
            text = page_obj.extract_text()
            print(text)
    return text


import requests
import tqdm


def upload_file(file_path, url):
    file = open(file_path, "rb")
    total_size = len(file.read())
    file.seek(0)

    headers = {
        'Content-Length': str(total_size),
        'Content-Type': 'video/mp4',
        # 'Authorization':
    }

    progress_bar = tqdm.tqdm(total=total_size, unit='B', unit_scale=True)

    for chunk in file:
        response = requests.post(url, data=chunk, headers=headers)
        progress_bar.update(len(chunk))

    progress_bar.close()
    file.close()



import uvicorn
from fastapi import Form, FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
import urllib.parse
import requests
import time
app = FastAPI(title="语音识别", version="v1.0", )

# 爬虫 www.iresearch.com.cn通过关键字范围搜索
@app.post(path='/scrapy_by_keyword')
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
    print(url)
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

        # /html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[1]
        url_back = res.xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]//a/@href").getall()
        urls = [pre_url + i for i in url_back]

        # /html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[2]/div[1]/a/img/@alt
        names = res.xpath("/html/body/div[1]/div[2]/div[2]/div/div/div[2]/div[1]/div[2]//a/img/@alt").getall()

        ids_url = [0, 2, 4, 6, 8, 10, 12, 14, 16]
        for i, val in enumerate(zip(ids_url, names)):
            dicts[urls[val[0]]] = val[1]

    return {"isSuc": True, "code": 0, "msg": "Success ~", "res": {"res": dicts}}


if __name__ == '__main__':
    # uvicorn.run(app, host="0.0.0.0", port=18511)

    # pdf2word(r"C:\Users\Xavier\Desktop\O域九天AI平台能力上台及能力运维培训-20220510-nj.pdf")
    # upload_file("./test/test.mp4", "http://0.0.0.0:18510")
    pass
    import uuid
    print(uuid.uuid1())
    # print(uuid.uuid3())
    print(uuid.uuid4())
