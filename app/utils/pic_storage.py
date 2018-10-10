import qiniu
from flask import current_app

access_key = 'W0oGRaBkAhrcppAbz6Nc8-q5EcXfL5vLRashY4SI'
secret_key = 'tsYCBckepW4CqW0uHb9RdfDMXRDOTEpYecJAMItL'
bucket_name = "python-ihome"

"""
使用方法：

oz6itywx9.bkt.clouddn.com/文件名称

"""


def pic_storage(data):
    """将图片数据保存到七牛云"""
    q = qiniu.Auth(access_key, secret_key)
    # 七牛给你指明的文件名称，默认别去设置，七牛会给你分配一个唯一图片名称
    token = q.upload_token(bucket_name)
    # 七牛上传二进制图片数据
    try:
        ret, info = qiniu.put_data(token, None, data)
        # print(ret, "&&" ,info)
    except Exception as e:
        current_app.logger.error(e)
        # 工具类的异常应该抛给调用者看
        raise e

    if info.status_code != 200:
        raise Exception("七牛云上传图片异常")

    # 上传成功，返回图片名称
    return ret["key"]


if __name__ == '__main__':
    file = input("请求输入图片地址：")
    with open(file, 'rb') as f:
        pic_storage(f.read())
