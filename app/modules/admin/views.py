from flask import render_template, request, current_app, session, g, redirect, url_for

from app import user_login_data
from app.models import User
from . import admin_bp


@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        # 获取session中指定的值
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        # 如果用户id存在,并且是管理员,那么直接跳转管理后台主页
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))
        return render_template('admin/login.html')

    # 取到登录的参数
    username = request.form.get("username")
    password = request.form.get("password")
    if not all([username, password]):
        return render_template('admin/login.html', errmsg='参数不足')

    try:
        user = User.query.filter(User.mobile == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="数据查询失败")

    if not user:
        return render_template('admin/login.html', errmsg="用户不存在")

    if not user.check_passowrd(password):
        return render_template('admin/login.html', errmsg='密码错误')

    if not user.is_admin:
        return render_template('admin/login.html', errmsg='用户权限错误')

    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    if user.is_admin:
        session['is_admin'] = True

    # 跳转到后台管理主页
    return redirect(url_for('admin.admin_index'))


@admin_bp.route('/')
@user_login_data
def admin_index():
    """
    站点主页
    :return:
    """
    # 读取登录用户的信息
    user = g.user
    # 优化进入主页逻辑:如果管理员进入主页,必须要登录状态,反之就引导到登录界面
    if not user:
        return redirect(url_for('admin.admin_login'))
    # 构造渲染数据
    data = {
        'user_info': user.to_dict()
    }
    # 渲染主页
    return render_template('admin/index.html', data=data)
