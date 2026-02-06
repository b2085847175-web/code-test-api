import sys
import os
# 添加项目根目录到 Python 路径，支持直接运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pytest
from api.chat import chat
from common.tool import get_token
from data.test_chat_data import test_chat_sessions

# 测试前获取一次 token，所有用例共享
TOKEN = get_token()

# 每轮对话后的等待时间（秒），等待 AI 回复落库后再发送下一个问题
WAIT_AFTER_REPLY = 10


def generate_username():
    """生成 tb_时间戳 格式的用户名"""
    return f"tb_{int(time.time() * 1000)}"


def extract_reply(result):
    """从响应中提取 AI 回复内容"""
    replies = [
        action['payload']['content']
        for action in result['data']['ai_actions']
        if action.get('actionType') == 'sendMessage'
    ]
    return '\n\n'.join(replies)


@pytest.mark.parametrize("session_name,messages", test_chat_sessions)
def test_chat_session(session_name, messages):
    """
    多轮对话测试：同一个用户连续发送多条消息
    服务端根据 username 自动维护对话历史，客户端只需传当前消息
    支持两种消息类型：
    1. 普通文本消息: {"txt": "你好"}
    2. 商品咨询消息: {"txt": "商品链接", "product": {"id": "...", "title": "...", "url": "..."}}
    """
    username = generate_username()
    print(f"\n{'='*50}")
    print(f"会话: {session_name}")
    print(f"用户: {username}")
    print(f"{'='*50}")

    for i, msg in enumerate(messages, 1):
        # 解析消息内容
        if isinstance(msg, dict):
            txt = msg['txt']
            product = msg.get('product')  # 商品信息（可选）
        else:
            txt = msg
            product = None

        print(f"\n--- 第 {i} 轮对话 ---")
        if product:
            print(f"用户: [发送商品] {product.get('title', txt)}")
        else:
            print(f"用户: {txt}")

        # 调用聊天接口（只传当前消息，服务端自动维护上下文）
        response = chat(txt, TOKEN, username, inquiry_product=product)
        result = response.json()

        # 基础断言
        assert result['code'] == 200, f"接口返回异常: {result['message']}"
        assert result['message'] == 'success'
        assert len(result['data']['ai_actions']) > 0, "AI 没有返回任何回复"

        # 提取 AI 回复
        full_reply = extract_reply(result)
        assert len(full_reply) > 0, "AI 回复内容为空"
        print(f"AI: {full_reply}")

        # 等待 AI 回复落库后再发送下一条消息
        if i < len(messages):
            print(f"等待 {WAIT_AFTER_REPLY} 秒...")
            time.sleep(WAIT_AFTER_REPLY)


if __name__ == "__main__":
    # 支持直接运行: python test_chat.py
    pytest.main([__file__, "-v", "-s"])