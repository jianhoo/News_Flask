from flask import Blueprint

# 创建蓝图,并设置蓝图前缀
passport_bp = Blueprint("passport", __name__,url_prefix='/passport')

from . import views