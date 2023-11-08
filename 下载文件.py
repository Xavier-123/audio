import requests
url = "http://192.168.12.84:18510/slice_video"
video_path = r"E:\work\AI_Project\audio\code2\test\test.mp4"
with open(video_path, 'rb')as f:
    files = {'file': f}
    data = {
        "start_time_min": 0,
        "start_time_second": 1,
        "end_time_min": 0,
        "end_time_second": 25,
    }
    r = requests.post(url, files=files, data=data)
    print(r)
    with open("./cache/download/test_2.mp4", 'wb') as f:
        f.write(r.content)


# from gtts import gTTS
# txt = "后续新增删除会话功能"
# language = 'zh'
# myobj = gTTS(text=txt, lang=language, slow=False)
# myobj.save("./gtts_test.mp3")


from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

text = '待合成文本'
# model_id = 'damo/speech_sambert-hifigan_tts_zh-cn_16k'
model_id = 'damo/speech_sambert-hifigan_tts_zhiyan_emo_zh-cn_16k'
sambert_hifigan_tts = pipeline(task=Tasks.text_to_speech, model=model_id)
output = sambert_hifigan_tts(input=text, voice='zhitian_emo')
wav = output[OutputKeys.OUTPUT_WAV]
with open('output.wav', 'wb') as f:
    f.write(wav)



# import pyttsx3
# engine = pyttsx3.init()
#
# voices = engine.getProperty('voices')
#
# for voice in voices:
#     print("Voice:")
#     print(" - ID: %s" % voice.id)
#     print(" - Name: %s" % voice.name)
#     print(" - Languages: %s" % voice.languages)
#     print(" - Gender: %s" % voice.gender)
#     print(" - Age: %s" % voice.age)
#
# # 设置语速与音量
# print(voices[1].id)
# engine.setProperty('voice', voices[1].id)
# # tts_engine.setProperty('voice', voices[1].id)
#
# # 保存语音
# # save_path = "./text2audio.mp3"
# engine.say("北京天气怎么样？")
# # engine.say("hello？")
# # engine.save_to_file("北京天气怎么样？", save_path)
# engine.runAndWait()
