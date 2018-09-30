from app.lib.yuntongxun.CCPRestSDK import REST
import ssl

ssl._create_default_https_context = ssl._create_unverified_context  # 全局取消证书验证

# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
accountSid = '8a216da8662360a40166242b579600c2'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
accountToken = '01c84ad138664c83b370c43609424fef'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
appId = '8a216da8662360a40166242b57f600c8'

# 说明：请求地址，生产环境配置成app.cloopen.com
serverIP = 'app.cloopen.com'

# 说明：请求端口 ，生产环境为8883
serverPort = '8883'

# 说明：REST API版本号保持不变
softVersion = '2013-12-26'


class CCP(object):
    """发送短信的辅助类"""

    def __new__(cls, *args, **kwargs):
        # 判断是否存在类属性_instance，_instance是类CCP的唯一对象，即单例
        if not hasattr(CCP, "instance"):
            cls.instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls.instance.rest = REST(serverIP, serverPort, softVersion)
            cls.instance.rest.setAccount(accountSid, accountToken)
            cls.instance.rest.setAppId(appId)
        return cls.instance

    def send_template_sms(self, to, datas, temp_id):
        """发送模板短信"""
        # @param to 手机号码
        # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
        # @param temp_id 模板Id
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        print(result)
        # 如果云通讯发送短信成功，返回的字典数据result中statuCode字段的值为"000000"
        if result.get("statusCode") == "000000":
            # 返回0 表示发送短信成功
            return 0
        else:
            # 返回-1 表示发送失败
            return -1


if __name__ == '__main__':
    ccp = CCP()
    ccp.send_template_sms("13590299759", {"123456", "5"}, "1")
