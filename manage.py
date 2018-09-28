from flask import current_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from Info import create_app,db

app = create_app('debug')

# 创建管理对象
manager = Manager(app)
# 数据库迁移
Migrate(app, db)
# 添加db命令
manager.add_command('db', MigrateCommand)


@app.route('/index')
def hello_world():
    current_app.logger.debug("debug")
    current_app.logger.error("error")
    return 'index'


if __name__ == '__main__':
    manager.run()
