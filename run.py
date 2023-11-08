# coding:utf-8
# @Author : wangxin
# @Date : 2022/3/21
# @Version : v1


import uvicorn

from conf.config import workers

if __name__ == '__main__':
    uvicorn.run(app='api:app', host="0.0.0.0", port=9000, workers=workers)
