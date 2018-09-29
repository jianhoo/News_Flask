from flask import request

from app.utils.response_code import RET
from . import passport_bp
from app.utils.captcha.captcha import captcha
from app import redis_store, constants
from flask import render_template, current_app, make_response, jsonify


@passport_bp.route('/image_code')
def get_image_code():
    """
    获取图片验证码
    :return:
    """
    # 1.获取当前的图片编号id
    code_id = request.args.get('code_id')
    # 2.生成验证码
    name, text, image, = captcha.generate_captcha()

    try:
        # 保存当前生成的图片验证码内容
        print(type(code_id))
        redis_store.setex('ImageCode_' + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))

    # 返回相应内容
    resp = make_response(image)
    # 设置内容类型
    resp.headers['Content-Type'] = 'image/jpg'
    return resp
