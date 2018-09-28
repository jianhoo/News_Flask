from flask import current_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db
from info import models

app = create_app('debug')

# 创建管理对象
manager = Manager(app)
# 数据库迁移
Migrate(app, db)
# 添加db命令
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
