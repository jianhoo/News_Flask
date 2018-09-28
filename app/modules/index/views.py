from . import index_bp
from flask import render_template


@index_bp.route('/')
def hello_world():
    # current_app.logger.debug("debug")
    # current_app.logger.error("error")
    return "index"