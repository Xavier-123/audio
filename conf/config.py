# coding:utf-8
# @Author : wangxin
# @Date : 2022/6/20
# @Version : v1

import os
import pathlib

# todo ========== 一、通用配置 ==========

# # 并发数
workers = int(os.environ.get("WORKERS", 1))
# # 使用cpu
use_cpu = int(os.environ.get("USE_CPU", 1))

# 缓存声音文件:用于debug
use_cache = bool(os.environ.get("CHAR_LOCATE", 0))

# 配置缓存目录(不存在时新建)
cache_dir = os.environ.get("CACHE_DIR", "./cache")
pathlib.Path(cache_dir).mkdir(parents=True, exist_ok=True)

# 切片保存目录
slice_dir = os.environ.get("SLICE_DIR", "./save")

# 模型最大输入长度
maximum_sequence_length = 513

# 大模型参数
large_model_ip = os.environ.get("LARGE_MODEL_IP", "192.168.12.84")
large_model_port = os.environ.get("LARGE_MODEL_PORT", "18123")
large_model_name = os.environ.get("LARGE_MODEL_NAME", "vicuna-13b-v1.5")
