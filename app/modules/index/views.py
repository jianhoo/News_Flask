from app import constants
from app.models import User, News
from . import index_bp
from flask import render_template, current_app, session


@index_bp.route('/')
def hello_world():
    # 获取到当前登录用户的id
    user_id = session.get("user_id")
    # 通过id获取用户信息
    user = None  # type = User
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 获取点击排行数据
    new_list = None
    try:
        new_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    click_news_list = []
    for news in new_list if new_list else []:
        click_news_list.append(news.to_basic_dict())

    data = {
        'user_info': user.to_dict() if user else None,
        'click_news_list': click_news_list
    }

    return render_template("news/index.html", data=data)


@index_bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")
