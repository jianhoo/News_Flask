from . import index_bp


@index_bp.route('/index')
def hello_world():
    # current_app.logger.debug("debug")
    # current_app.logger.error("error")
    return 'index'