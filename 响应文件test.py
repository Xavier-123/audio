# coding:utf-8
# @Author : wangxin
# @Date : 2023/02/06
# @Version : v1

import pathlib
import time

import requests


def main():
    url = 'http://127.0.0.1:9000/md_bytes'
    file_path = 'xxx.md'
    # url = "http://192.168.12.84:18506"
    # file_path = 'code/api.py'

    file_name = pathlib.Path(file_path).name
    binary_io = open(file_path, 'rb')
    file_type = 'file/md'
    files = {'bytes_file': (file_name, binary_io, file_type)}
    print("请求...", url)
    r = requests.post(url, files=files)

    # return r.json()
    return r


if __name__ == '__main__':
    t = time.time()
    res2 = main()
    print(time.time() - t)
    print(res2)
    with open("aaa.pptx", "wb") as f:
        f.write(res2.content)
