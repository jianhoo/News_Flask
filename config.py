import redis


class Config(object):
    """项目配置信息"""
    # 配置连接的数据库
    SQLALCHEMY_DATABASE_URI = "mysql+dbmysql://root:A92b11c20@127.0.0.1:3306/information"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 配置redis数据库
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask__session的配置信息
    SECRET_KEY = "1234567890"
    SESSION_TYPE = "redis"  # 指定session保存到redis中
    SESSION_USE_SIGNER = True  # 让cookie中的seesion_id 被加密签名处理
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期,单位是秒


class DebugConfig(Config):
    """测试环境下的配置"""
    DEBUG = True


class ReleaseConfig(Config):
    """正式环境下的配置"""
    pass


config = {
    "debug": DebugConfig,
    "release": ReleaseConfig
}