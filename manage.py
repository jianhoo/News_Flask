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
        current_app.logger.error(e)
        db.session.rollback()




if __name__ == '__main__':
    manager.run()
