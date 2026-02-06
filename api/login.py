from requests import session


def login(account, password):
    """登录接口，返回响应对象"""
    url = "https://dev.zhiyan.chat/api/auth/login"
    body = {
        "account": account,
        "password": password
    }
    return session().post(url=url, json=body)
