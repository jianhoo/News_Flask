from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
import redis
from config import Config

app = Flask(__name__)


# 设置app应用的config配置
app.config.from_object(Config)
# 构建数据库对象
db = SQLAlchemy(app)
# 构建redis数据库对象
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
Session(app)

# 创建管理对象
manager = Manager(app)
Migrate(app, db)
# 添加db命令
manager.add_command('db', MigrateCommand)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
