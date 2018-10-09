from app import constants, db
from app.models import News, Comment
from app.utils.common import user_login_data
from app.utils.response_code import RET
from . import news_bp
from flask import render_template, current_app, abort, g, request, jsonify


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

    # 判断是否收藏该新闻,默认值为false
    is_collected = False
    # 判断用户是否收藏过该新闻
    if g.user:
        if cur_news in g.user.collection_news:
            is_collected = True

    # 获取当前新闻评论
    comments = []
    try:
        comments = (Comment.query.filter(Comment.news_id == news_id)) \
            .order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="评论查询失败")

    comment_list = []
    for item in comments:
        comment_list.append(item.to_dict())

    data = {
        "news": cur_news.to_dict(),
        "user_info": g.user.to_dict() if g.user else None,
        "click_news_list": click_news_list,
        "is_collected": is_collected,
        "comments": comment_list
    }
    return render_template('news/detail.html', data=data)


@news_bp.route("/news_collect", methods=['POST'])
@user_login_data
def news_collect():
    """新闻收藏"""

    user = g.user
    json_data = request.json
    print(type(json_data))
    news_id = json_data.get("news_id")
    action = json_data.get("action")

    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ("collect", "cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="查询数据失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    if action == "collect":
        user.collection_news.append(news)
    else:
        user.collection_news.remove(news)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=RET.OK, errmsg="操作成功")


@news_bp.route("/news_comment", methods=['POST'])
@user_login_data
def add_news_comment():
    """添加评论"""
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登陆")
    # 获取参数
    data_dict = request.json
    news_id = data_dict.get("news_id")
    comment_str = data_dict.get("comment")
    parent_id = data_dict.get("parent_id")

    if not all([news_id, comment_str]):
        jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该新闻不存在")

    # 初始化模型,保存数据
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news_id
    comment.content = comment_str

    if parent_id:
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存评论数据失败")

    # 返回响应
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())
