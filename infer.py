from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import time

t1 = time.time()
inference_pipeline = pipeline(
    task=Tasks.auto_speech_recognition,
    # model='damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
    model='damo/speech_paraformer-large-vad-punc_asr_nat-zh-cn-16k-common-vocab8404-pytorch',   # 这个模型集成了VAD、ASR、标点模型
    # vad_model='damo/speech_fsmn_vad_zh-cn-16k-common-pytorch',
    # punc_model='damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch',
    # lm_model='damo/speech_transformer_lm_zh-cn-common-vocab8404-pytorch',
    # lm_weight=0.15,
    # beam_size=10,
    output_dir='./decode_dir'
)

rec_result = inference_pipeline(audio_in='./cache/test.mp3')
t2 = time.time()
print(t2 - t1)
print(rec_result)




# # 分开跑
# inference_pipeline = pipeline(
#     task=Tasks.auto_speech_recognition,
#     model='damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch',
#     output_dir='./decode_dir'
# )
# rec_result = inference_pipeline(audio_in='./cache/test.mp3')
# print(rec_result)
# print(rec_result["text"])
#
# inference_pipeline = pipeline(
#     task=Tasks.punctuation,
#     model='damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch',
# )
# rec_result_ = inference_pipeline(text_in=rec_result["text"])
# print(rec_result_)
