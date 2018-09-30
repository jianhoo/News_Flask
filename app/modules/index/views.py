from app.models import User
from . import index_bp
from flask import render_template, current_app, session


@index_bp.route('/')
def hello_world():
    # 获取到当前登录用户的id
    user_id = session.get("user_id")
    # 通过id获取用户信息
    user = None  # type=User
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    return render_template("news/index.html", data={"user_info": user.to_dict() if user else None})


@index_bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")
