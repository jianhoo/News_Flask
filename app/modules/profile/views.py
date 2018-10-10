from flask import g, redirect, render_template, request, jsonify, current_app, session
from app import user_login_data, db
from app.utils.response_code import RET
from . import profile_bp


@profile_bp.route('/info')
@user_login_data
def get_user_info():
    """
    获取用户信息
    1.获取到当前登录的用户模型
    2.返回模型中的指定内容
    :return:
    """

    user = g.user
    if not user:
        # 用户未登录,重定向到主页
        return redirect('/')

    data = {
        "user_info": user.to_dict()
    }

    return render_template("profile/user.html", data=data)


@profile_bp.route("/base_info", methods=["GET", "POST"])
@user_login_data
def get_base_info():
    """
    用户基本信息
    1.获取用户登录信息
    2.获取到传入参数
    3.更新并保存数据
    4.返回结果
    :return:
    """
    # 1.获取当前登录用户的信息
    user = g.user
    # 判断是否为get方法,若是则直接返回用户信息
    if request.method == "GET":
        return render_template("profile/user_base_info.html", data={"user_info": user.to_dict()})

    # 2.获取到传入参数
    data_dict = request.json
    nick_name = data_dict.get("nick_name")
    gender = data_dict.get("gender")
    signature = data_dict.get("signature")
    if not all([nick_name, gender, signature]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    if gender not in (["MAN", "WOMAN"]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 3.更新并保存数据
    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 讲session中保存的数据进行事实更新
    session["nick_name"] = nick_name
    return jsonify(errno=RET.OK, errmsg="更新成功")
