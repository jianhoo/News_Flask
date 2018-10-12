import random
import re

from datetime import datetime
from flask import request, session

from app.lib.yuntongxun.cpp import CCP
from app.models import User
from app.utils.response_code import RET
from . import passport_bp
from app.utils.captcha.captcha import captcha
from app import redis_store, constants, db
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
        redis_store.setex('ImageCode_' + code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return make_response(jsonify(errno=RET.DATAERR, errmsg='保存图片验证码失败'))

    # 返回相应内容
    resp = make_response(image)
    # 设置内容类型
    resp.headers['Content-Type'] = 'image/jpg'
    return resp


@passport_bp.route('/smscode', methods=['POST'])
def send_sms():
    """
        1. 接收参数并判断是否有值
        2. 校验手机号是正确
        3. 通过传入的图片编码去redis中查询真实的图片验证码内容
        4. 进行验证码内容的比对
        5. 生成发送短信的内容并发送短信
        6. redis中保存短信验证码内容
        7. 返回发送成功的响应
        :return:
        """
    # 1.获取参数,并判断参数是否有值
    param_dict = request.json
    mobile = param_dict.get("mobile")
    image_code = param_dict.get('image_code')
    image_code_id = param_dict.get("image_code_id")

    # 判断参数是否齐全
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 2.校验手机号是否正确
    print(mobile)
    # 2. 校验手机号是正确
    if not re.match("^1[3578][0-9]{9}$", mobile):
        # 提示手机号不正确
        return jsonify(errno=RET.DATAERR, errmsg="手机号不正确")

    # 3.通过传入的图片编码去redis中查询真实的图片验证码内容
    try:
        real_image_code = redis_store.get("ImageCode_" + image_code_id)
    except Exception as e:
        current_app.looger.error(e)
        # 获取图片验证码失败
        return jsonify(errno=RET.DBERR, errmsg="获取图片验证码失败")

    # 3.1判断验证码是否存在,已过期
    if not real_image_code:
        # 验证码已过期
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")

    # 4.进行验证码内容的比对
    if image_code.lower() != real_image_code.lower():
        # 验证码输入错误
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 4.1校验该手机是否已经注册
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败")
    if user:
        # 该手机已被注册
        return jsonify(errno=RET.DATAEXIST, errmsg="该手机已被注册")

    # 5. 生成发送短信的内容并发送短信
    result = random.randint(0, 999999)
    sms_code = "%06d" % result
    current_app.logger.debug("短信验证码的内容:%s" % sms_code)
    ccp = CCP()
    result = ccp.send_template_sms(mobile,
                                   {sms_code, "5"}, "1")
    if result != 0:
        # 发送短信失败
        return jsonify(errno=RET.THIRDERR, errmsg="发送短信失败")

    # 6.redis中保存短信验证码内容
    try:
        redis_store.set("SMS_" + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")

    # 7.返回发送成功的响应
    return jsonify(errno=RET.OK, errmsg="发送成功")


@passport_bp.route('/register', methods=['POST'])
def register():
    """
    1.获取参数和判断是否有值
    2.从redis中获取指定手机号对应的短信验证码的
    3.校验验证码
    4.初始化user模型, 并设置数据并添加到数据库
    5.保存当前用户的状态
    6.返回注册的结果
    :return:
    """

    # 1.获取参数和判断是否有值
    param_data = request.json
    mobile = param_data.get("mobile")
    sms_code = param_data.get("smscode")
    password = param_data.get("password")

    if not all([mobile, sms_code, password]):
        # 参数不全
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 2.从redis中获取指定手机号对应的短信验证码的
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取本地校验码失败")

    if not real_sms_code:
        # 短信验证码过期
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期")

    # 3.校验验证码
    if sms_code != real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    # 删除短信验证码
    try:
        redis_store.delete("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 4.初始化user原型,并设置数据并添加到数据库
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    # 对密码进行处理
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        # 数据保存错误
        return jsonify(errno=RET.DATAERR, errmsg="数据保存错误")

    # 5.保存用户登录状态
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    if user.is_admin:
        session["is_admin"] = True

    # 6.返回注册结果
    return jsonify(errno=RET.OK, errmsg="OK")


@passport_bp.route('/login', methods=['POST'])
def login():
    """
    1.获取参数和判断是否有值
    2.从数据库查询出指定的用户
    3.校验密码
    4.保存用户登录状态
    5.返回结果
    :return:
    """

    # 1.获取参数和判断是否有值
    param_data = request.json
    mobile = param_data.get('mobile')
    password = param_data.get("password")

    if not all([mobile, password]):
        # 参数不全
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 2.从数据库查询出指定的用户
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据错误")

    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")

    # 3.校验密码
    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    # 4.保存用户登录状态
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    if user.is_admin:
        session["is_admin"] = True
    # 记录用户最后一次登录时间
    user.last_login = datetime.now()

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)

    # 5.登录成功
    return jsonify(errno=RET.OK, errmsg="OK")


@passport_bp.route('/logout', methods=["POST"])
def logout():
    """
    清除session中的对应登录之后保存的信息
    :return:
    """
    session.pop('user_id', None)
    session.pop('nick_name', None)
    session.pop('mobile', None)
    session.pop('is_admin', None)

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="OK")

