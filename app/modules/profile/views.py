from flask import g, redirect, render_template, request, jsonify, current_app, session
from app import user_login_data, db, constants
from app.models import Category, News
from app.utils.pic_storage import pic_storage
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


@profile_bp.route("/pic_info", methods=["GET", "POST"])
@user_login_data
def pic_info():
    user = g.user
    if request.method == "GET":
        return render_template("profile/user_pic_info.html", data={"user_info": user.to_dict()})

    # 1.获取到上传的文件
    try:
        avatar_file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="读取文件出错")

    # 2.再将文件上传到奥七牛云
    try:
        url = pic_storage(avatar_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

    # 设置用户模块相关数据
    user.avatar_url = url
    # 将数据保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据存储有误")

    # 4.返回上传的结果<avatar_url>
    return jsonify(errno=RET.OK, errmsg="图片保存成功",
                   data={"avatar_url": constants.QINIU_DOMIN_PREFIX + url})


@profile_bp.route("/pass_info", methods=["GET", "POST"])
@user_login_data
def pass_info():
    if request.method == "GET":
        return render_template("profile/user_pass_info.html")

    # 1.获取到传入参数
    data_dict = request.json
    old_password = data_dict.get("old_password")
    new_password = data_dict.get("new_password")

    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 2.获取当前登录用户的信息
    user = g.user

    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码有误")

    # 更新数据
    user.password = new_password
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    return jsonify(errno=RET.OK, errmsg="保存成功")


@profile_bp.route("/collection")
@user_login_data
def user_collection():
    # 获取页数
    page_num = request.args.get("p", 1)
    try:
        page_num = int(page_num)
    except Exception as e:
        current_app.logger.error(e)
        page_num = 1

    user = g.user
    collections = []
    current_page = 1
    total_page = 1

    try:
        # 进行分页数据查询
        paginate = user.collection_news.paginate(page_num, constants.USER_COLLECTION_MAX_NEWS, False)
        # 获取分页数据
        collections = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    collection_dict_li = []
    for news in collections:
        collection_dict_li.append(news.to_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "collections": collection_dict_li
    }

    return render_template("profile/user_collection.html", data=data)


@profile_bp.route("/news_release", methods=["GET", "POST"])
@user_login_data
def news_release():
    if request.method == "GET":
        categories = []
        try:
            # 获取所有的分类数据
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        # 定义列表保存分类数据
        categories_dict_list = []

        for category in categories:
            # 获取字典
            cate_dict = category.to_dict()
            # 拼接内容
            categories_dict_list.append(cate_dict)

        # 移除"最新"分类
        categories_dict_list.pop(0)

        data = {
            "categories": categories_dict_list
        }
        # 返回内容
        return render_template('profile/user_news_release.html', data=data)

    # POST提交,执行发布新闻操作

    # 1.获取要提交的数据
    title = request.form.get("title")
    source = "个人发布"
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")
    # 1.1判断数据是否有值
    if not all([title, source, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 1.2尝试读取图片
    try:
        index_image = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 2.将标题图片上传到七牛
    try:
        key = pic_storage(index_image)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片失败")

    # 3.初始化新闻模型,并设置相关数据
    news = News()
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = g.user.id
    # 1代表待审核状态
    news.status = 1

    # 4.保存到数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 5.返回结果
    return jsonify(errno=RET.OK, errmsg="发布成功,等待审核")
