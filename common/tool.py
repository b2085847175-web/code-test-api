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


def get_product_for_chat(token, shop_id="585", index=0):
    """
    便捷方法：获取指定店铺的商品，直接返回可传给 chat 的 inquiry_product 格式
    
    参数:
        token: 登录 token
        shop_id: 店铺ID，默认 585（儒意化妆品旗舰店）
        index: 商品索引，默认第0个
    
    返回:
        dict: {"id": "...", "title": "...", "url": "..."} 或 None
    """
    from api.product import get_product_by_index
    return get_product_by_index(token, shop_id, index)
