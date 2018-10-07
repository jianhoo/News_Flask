import logging
from logging.handlers import RotatingFileHandler

from redis import StrictRedis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

from flask_wtf.csrf import CSRFProtect, generate_csrf

from app.utils.common import do_index_class
from config import config_dict

db = SQLAlchemy()
redis_store = None  # type:StrictRedis


def setup_log(config_name):
    """配置日志"""
    # 设置日志的记录等级
    logging.basicConfig(level=config_dict[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """通过传入不同的配置名字,初始化其对应配置的应用实例"""
    app = Flask(__name__)
    setup_log(config_name)

    # 设置app应用的config配置
    app.config.from_object(config_dict[config_name])
    # 构建数据库对象
    db.init_app(app)
    # 构建redis数据库对象
    global redis_store
    redis_store = StrictRedis(host=config_dict[config_name].REDIS_HOST,
                              port=config_dict[config_name].REDIS_PORT,
                              decode_responses=True)

    # 开启csrf保护
    CSRFProtect(app)

    # 每个post请求带上csrf_token参数
    @app.after_request
    def after_request(response):
        # 调用函数生成csrf_token
        csrf_token = generate_csrf()
        # 通过cookie将值传给前端
        response.set_cookie("csrf_token", csrf_token)
        return response

    # 设置session保存位置
    Session(app)

    # 添加自定义过滤器
    app.add_template_filter(do_index_class, "index_class")

    # 首页蓝图注册
    register_index(app)
    # 登录注册模块的蓝图注册
    register_passport(app)

    return app


def register_passport(app):
    from app.modules.passport import passport_bp
    app.register_blueprint(passport_bp)


def register_index(app):
    # 注册蓝图
    from app.modules.index import index_bp
    app.register_blueprint(index_bp)
