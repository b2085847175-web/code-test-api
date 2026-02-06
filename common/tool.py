from api.login import login

DEFAULT_ACCOUNT = "zhaowenlong"
DEFAULT_PASSWORD = "init@2234"


def get_token(account=DEFAULT_ACCOUNT, password=DEFAULT_PASSWORD):
    """登录并返回 accessToken"""
    result = login(account, password).json()
    return result['data']['accessToken']


def get_headers(token):
    """生成带 Authorization 的请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
