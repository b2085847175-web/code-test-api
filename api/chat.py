import time
import uuid
from requests import session
from common.tool import get_headers


def chat(txt, token, username="tb_1770348369683", inquiry_product=None):
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
    """
    url = "https://dev.zhiyan.chat/chat/answer"
    now = int(time.time())
    
    body = {
        "platform": "tmall",
        "shop_name": "儒意化妆品旗舰店",
        "account": "测试专用1",
        "username": username,
        "shop_id": "585",
        "is_test": True,
        "last_order_time": now,
        "last_order_info": None,
        "request_id": str(uuid.uuid4()),
        "inquiry_product": inquiry_product or {},
        "messages": [
            {
                "role": "user",
                "content": txt,
                "created_at": now
            }
        ]
    }
    headers = get_headers(token)
    return session().post(url=url, json=body, headers=headers)

