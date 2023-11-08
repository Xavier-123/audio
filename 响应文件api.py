# coding:utf-8
# @Author : wangxin
# @Date : 2023/02/03
# @Version : v1
import base64
import pathlib
import time
import uuid
from typing import Optional

import uvicorn
from fastapi import FastAPI, status
from fastapi import File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.requests import Request
from starlette.responses import FileResponse

from main.error_define import CustomError
from main.log import logger
from mdtree.tree2ppt import Tree2PPT

app = FastAPI(title="MD2PPT", version="v1.0", )

tree2ppt = Tree2PPT()


class RequestModel(BaseModel):
    # MD字符串
    strs: str = Field(...,
                      example="# 第六章  投标文件格式\n\n## 一、投标文件封面\n\n     （项目名称）    标包服务集中招标   \n\n \n\n投标文件   部分\n\n\n\n## 二、评标索引表\n\n## 三、投标函\n...",
                      description="Markdown格式的文本字符串")

    # PPT主题:
    theme: Optional[str] = Field("branch",
                                 title="主题",
                                 description="主题必须从以下列表中选择",
                                 examples=['branch', 'color', 'desk', 'lion', 'pencil', 'pink', 'plants', 'run',
                                           'trees', 'water-color'],
                                 example="branch",
                                 )

    # 当前字体
    font_name: str = Field("微软雅黑", example="微软雅黑", title="内容字体")
    title_font_size: int = Field(26, example=26, title="标题字号")
    content_font_size: int = Field(18, example=18, title="内容字号")

    # 主题字体字号 (PPT第一页包括 报告标题 报告人等信息)
    # theme_font_name: str = Field("微软雅黑", example="微软雅黑", title="主题字体")
    # theme_font_size: int = Field(26, example=26, title="主题字号")
    #
    # # 目录字体字号
    # contents_font_name: str = Field("微软雅黑", example="微软雅黑", title="目录字体")
    # contents_font_size: int = Field(26, example=26, title="目录字号")

    # 章节(标题)字体字号
    # title_font_name: str = Field("微软雅黑", example="微软雅黑", title="标题字体")
    # title_font_size: int = Field(26, example=26, title="标题字号")

    # 内容字体字号
    # content_font_name: str = Field("微软雅黑", example="微软雅黑", title="内容字体")
    # content_font_size: int = Field(18, example=18, title="内容字号")


class ResponseModel(BaseModel):
    isSuc: bool = Field(True, example=True)
    code: int = Field(0, example=0)
    msg: str = Field("Succeed", example="Succeed~")
    res: dict = Field({}, example={})


def getBase64stringFromFilepath(filepath):
    with open(filepath, 'rb') as f:
        img_byte = base64.b64encode(f.read())
    img_str = img_byte.decode('ascii')

    return img_str


def getASCIIstringFromFilepath(filepath):
    with open(filepath, 'rb') as f:
        s = f.read().decode("ascii")

    return s


@app.post(path='/md_strs', summary="string", response_model=ResponseModel, tags=["MD字符串上传接口"])
async def interface(req: RequestModel):
    # 解析参数
    file_str = req.strs
    theme = req.theme

    kwargs = dict(font_name=req.font_name,
                  font_title_size=req.title_font_size,
                  font_content_size=req.content_font_size)

    # 输出pptx文档的路径
    file_name = str(uuid.uuid4().hex) + ".pptx"
    src_path = pathlib.Path(".cache", file_name).as_posix()
    # 输出PPT
    tree2ppt.main(file_str, src_path, theme, **kwargs)

    return FileResponse(src_path, )
    #
    # file_base64 = getASCIIstringFromFilepath(src_path)
    #
    # content = {"isSuc": True, "code": 0, "msg": "Success ~",
    #            "res": {"file_name": file_name, "file_base64": file_base64}}
    #
    # logger.info(content)
    #
    # return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@app.post(path='/md_bytes', summary="bytes", response_model=ResponseModel, tags=["MD文件上传接口"])
async def interface(bytes_file: bytes = File()):
    # 解码Markdown文件流
    file_str = bytes_file.decode().replace("\r\n", "\n")
    print(file_str)
    # 输出pptx文档的路径
    file_name = str(uuid.uuid4().hex) + ".pptx"
    src_path = pathlib.Path(".cache", file_name).as_posix()  # 输出PPT
    # 输出PPT
    tree2ppt.main(file_str, src_path)

    return FileResponse(src_path)

    # file_base64 = getASCIIstringFromFilepath(src_path)
    #
    # content = {"isSuc": True, "code": 0, "msg": "Success ~",
    #            "res": {"file_name": file_name, "file_base64": file_base64}}
    #
    # logger.info(content)
    #
    # return JSONResponse(status_code=status.HTTP_200_OK, content=content)
    #


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    elapsed_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{elapsed_time:.3f}"

    return response


# 自定义错误
@app.exception_handler(CustomError)
async def unexcept_exception_handler(_: Request, exc: CustomError):
    content = {"isSuc": False, "code": exc.code, "msg": str(exc), "res": {}}
    logger.error(f"{content}")

    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


# 意料之外的错误
@app.exception_handler(Exception)
async def unexcept_exception_handler(_: Request, exc: Exception):
    content = {"isSuc": False, "code": -1, "msg": str(exc), "res": {}}
    logger.error(f"{content}")

    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=9000)
