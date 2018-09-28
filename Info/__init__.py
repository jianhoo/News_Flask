import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()


def create_app(config_name):
    """通过传入不同的配置名字,初始化其对应配置的应用实例"""

    app = Flask(__name__)

    # 设置app应用的config配置
    app.config.from_object(Config)
    # 构建数据库对象
    db.init_app(app)
    # 构建redis数据库对象
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
    # 开启csrf保护
    CSRFProtect(app)
    # 设置session保存位置
    Session(app)

    return app
