from flask import Blueprint, request, url_for, session, redirect

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

from . import views


@admin_bp.before_request
def before_request():
    # 判断如果不是登录页面的请求
    if not request.url_root.endswith(url_for('admin.admin_login')):
        user_id = session.get('user_id')
        is_admin = session.get('is_admin', False)

        if not user_id or not is_admin:
            # 判断当前是否有用户的登录,或者是否是管理员,如果不是,直接重定向到项目主页
            return redirect('/')
