import time
import uuid
from requests import session
from common.tool import get_headers


def chat(txt, token, username="tb_1770348369683", inquiry_product=None, shop_id="585",
         shop_name="儒意化妆品旗舰店", account="测试专用1", platform="tmall", full_messages=None):
    """
    聊天接口，需传入 token 和 username
    服务端会根据 username 自动维护对话历史，客户端只需传当前消息
    
    参数:
        txt: 用户发送的消息内容（文本或商品链接）
        token: 登录 token
        username: 用户名（自动生成 tb_时间戳 格式，同一用户保持一致以维持上下文）
        inquiry_product: 咨询的商品信息（可选），格式:
            {
                "id": "商品ID",
                "title": "商品标题",
                "url": "商品链接"
            }
        shop_id: 店铺ID，默认 585
        shop_name: 店铺名称，默认 儒意化妆品旗舰店
        account: 账号名称，默认 测试专用1
        platform: 平台，默认 tmall
        full_messages: 完整对话历史列表（可选），如果传了就直接用它构造body，否则保持原单条逻辑
    """
    url = "https://dev.zhiyan.chat/chat/answer"
    now = int(time.time())
    
    body = {
        "platform": platform,
        "shop_name": shop_name,
        "account": account,
        "username": username,
        "shop_id": shop_id,
        "is_test": False,
        "last_order_time": now,
        "last_order_info": None,
        "request_id": str(uuid.uuid4()),
        "inquiry_product": inquiry_product or {},
        "messages": full_messages if full_messages is not None else [
            {
                "role": "user",
                "content": txt,
                "created_at": now
            }
        ]
    }
    headers = get_headers(token)
    return session().post(url=url, json=body, headers=headers)


def chat_with_product(txt, token, username="tb_1770348369683", shop_id="585",
                      product_index=0, **kwargs):
    """
    带商品信息的聊天接口 —— 自动从商品列表获取商品，传给 AI

    参数:
        txt: 用户发送的消息内容
        token: 登录 token
        username: 用户名
        shop_id: 店铺ID，默认 585
        product_index: 商品在列表中的索引，默认第0个
        **kwargs: 其他传给 chat() 的参数（shop_name, account, platform 等）

    返回:
        响应对象
    """
    from api.product import get_product_by_index

    product = get_product_by_index(token, shop_id, index=product_index)
    if product:
        print(f"已自动获取商品: [{product['id']}] {product['title']}")
    else:
        print("未获取到商品信息，将不带商品进行提问")

    return chat(txt, token, username, inquiry_product=product, shop_id=shop_id, **kwargs)


def chat_with_product_id(txt, token, username="tb_1770348369683", shop_id="585",
                         product_id="", **kwargs):
    """
    带商品信息的聊天接口 —— 根据商品ID获取商品，传给 AI

    参数:
        txt: 用户发送的消息内容
        token: 登录 token
        username: 用户名
        shop_id: 店铺ID，默认 585
        product_id: 商品ID（字符串或数字）
        **kwargs: 其他传给 chat() 的参数（shop_name, account, platform 等）

    返回:
        响应对象
    """
    from api.product import get_product_by_id

    product = get_product_by_id(token, shop_id, product_id=product_id)
    if product:
        print(f"已通过商品ID获取商品: [{product['id']}] {product['title']}")
    else:
        print("未获取到商品信息，将不带商品进行提问")

    return chat(txt, token, username, inquiry_product=product, shop_id=shop_id, **kwargs)
