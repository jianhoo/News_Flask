from app import constants
from app.models import News
from app.utils.common import user_login_data
from . import news_bp
from flask import render_template, current_app, abort, g


@news_bp.route("/<int:news_id>")
@user_login_data
def news_detail(news_id):

    try:
        cur_news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    if not cur_news:
        # 返回数据未找到的页面
        abort(404)

        cur_news.clicks += 1

    # 获取点击排行数据
    new_list = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    click_news_list = []
    for news in news_list if news_list else []:
        click_news_list.append(news.to_dict())

    data = {
        "news": cur_news.to_dict(),
        "user_info": g.user.to_dict() if g.user else None,
        "click_news_list": click_news_list
    }
    return render_template('news/detail.html', data=data)