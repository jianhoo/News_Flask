import random
from datetime import datetime, timedelta

from flask import current_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app import models
from app import constants
from app.models import User

app = create_app('debug')

# 创建管理对象
manager = Manager(app)
# 数据库迁移
Migrate(app, db)
# 添加db命令
manager.add_command('db', MigrateCommand)


@manager.option('-u', '-name', dest='name')
@manager.option('-p', '-password', dest='password')
def createsuperuser(name, password):
    """创建管理员用户"""
    if not all([name, password]):
        print("参数不足")
        return

    user = User()
    user.mobile = name
    user.nick_name = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
        print("创建成功")
    except Exception as e:
        print(e)
        db.session.rollback()


# def add_test_users():
"""添加测试数据"""
#     users = []
#     now = datetime.now()
#     for num in range(0, 10000):
#         try:
#             user = User()
#             user.nick_name = "%011d" % num
#             user.mobile = "%011d" % num
#             user.password_hash = "pbkdf2:sha256:50000$zJaie0BI$789ea9d1cda600adcffc8940031e6ece76c91768db49aab7747d45ff2a83b02a"
#             user.last_login = now - timedelta(seconds=random.randint(0, 2678400))
#             users.append(user)
#             print(user.mobile)
#         except Exception as e:
#             print(e)
#
#     with app.app_context():
#         db.session.add_all(users)
#         db.session.commit()
#     print('OK')


if __name__ == '__main__':
    manager.run()
