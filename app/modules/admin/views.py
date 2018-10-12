import time
from datetime import datetime, timedelta

from flask import render_template, request, current_app, session, g, redirect, url_for, jsonify

from app import user_login_data, constants, db
from app.models import User, News
from app.utils.response_code import RET
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


@admin_bp.route('/user_count')
def user_count():
    # 查询总人数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询月新增数
    mon_count = 0
    try:
        now = time.localtime()
        mon_begin = '%d-%02d-01' % (now.tm_year, now.tm_mon)
        mon_begin_date = datetime.strptime(mon_begin, '%Y-%m-%d')
        mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询日新增数
    day_count = 0
    try:
        day_begin = '%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)
        day_begin_date = datetime.strptime(day_begin, '%Y-%m-%d')
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询图标信息
    # 获取到当天00:00:00时间
    now_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    # 定义空数组,保存数组
    active_date = []
    active_count = []

    # 依次添加数据,再反转
    for i in range(0, 31):
        begin_date = now_date - timedelta(days=i)
        end_date = now_date - timedelta(days=(i - 1))
        active_date.append(begin_date.strftime('%Y-%m-%d'))
        count = 0
        try:
            count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                      User.last_login < end_date).count()
        except Exception as e:
            current_app.logger.error(e)

        active_count.append(count)

    active_date.reverse()
    active_count.reverse()

    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_date": active_date,
        "active_count": active_count
    }

    return render_template('admin/user_count.html', data=data)


@admin_bp.route('/user_list')
def user_list():
    """获取用户列表"""

    # 获取参数
    page = request.args.get('p', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 设置变量默认值
    users = []
    current_page = 1
    total_page = 1

    # 查询数据
    try:
        paginate = User.query.filter(User.is_admin == False) \
            .order_by(User.last_login.desc()) \
            .paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)
        users = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 将模型列表转成字典列表
    users_list = []
    for user in users:
        users_list.append(user.to_admin_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "users": users_list
    }

    return render_template("admin/user_list.html", data=data)


@admin_bp.route('/news_review')
def news_review():
    """返回待审核新闻列表"""

    page = request.args.get("p", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_list = []
    current_page = 1
    total_page = 1

    try:
        paginate = News.query.filter(News.status != 0) \
            .order_by(News.create_time.desc()) \
            .paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_review_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_list": news_dict_list
    }

    return render_template('admin/news_review.html', data=data)


@admin_bp.route('/news_review_detail', methods=["GET", "POST"])
def news_review_detail():
    """新闻审核"""
    if request.method == "GET":
        # 获取新闻id
        news_id = request.args.get("news_id")
        if not news_id:
            return render_template("admin/news_review_detail.html", data={"errmsg", "未查询到该新闻"})

        # 通过id查询新闻
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)

        if not news:
            return render_template("admin/news_review_detail.html", data={"errmsg", "未查询到该新闻"})

        # 返回数据
        data = {
            "news": news.to_dict()
        }
        return render_template("admin/news_review_detail.html", data=data)

    # 执行审核操作

    # 1.获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")

    # 2.判断参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ("accept", "reject"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    news = None
    try:
        # 3.查询新闻
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到数据")

    # 4.根据不同的状态设置不同的值
    if action == "accept":
        news.status = 0
    else:
        # 拒绝通过,需要获取原因
        reason = request.json.get("reson")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        news.reason = reason
        news.status = -1

    # 保存数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=RET.OK, errmsg="操作成功")
