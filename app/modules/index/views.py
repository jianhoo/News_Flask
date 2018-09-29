from . import index_bp
from flask import render_template, current_app


@index_bp.route('/')
def hello_world():
    # current_app.logger.debug("debug")
    # current_app.logger.error("error")
    return render_template('news/index.html')


@index_bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")