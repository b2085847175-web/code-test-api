import sys
import os
# 添加项目根目录到 Python 路径，支持直接运行
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import random
import pytest
import allure
from api.chat import chat
from api.product import get_products
from common.tool import get_token
from data.test_chat_data import test_chat_sessions, product_questions

# Allure 结果输出目录
ALLURE_RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "allure-results")

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


def safe_print(text):
    """安全打印，自动处理 Windows 终端无法编码的字符（如 emoji）"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))


@allure.feature("多轮对话")
@pytest.mark.parametrize("session_name,messages", test_chat_sessions)
def test_chat_session(session_name, messages):
    """
    多轮对话测试：同一个用户连续发送多条消息
    服务端根据 username 自动维护对话历史，客户端只需传当前消息
    支持两种消息类型：
    1. 普通文本消息: {"txt": "你好"}
    2. 商品咨询消息: {"txt": "商品链接", "product": {"id": "...", "title": "...", "url": "..."}}
    """
    allure.dynamic.story(session_name)
    allure.dynamic.title(f"多轮对话 - {session_name}")

    username = generate_username()
    allure.attach(username, name="用户名", attachment_type=allure.attachment_type.TEXT)

    for i, msg in enumerate(messages, 1):
        # 解析消息内容
        if isinstance(msg, dict):
            txt = msg['txt']
            product = msg.get('product')
        else:
            txt = msg
            product = None

        with allure.step(f"第 {i} 轮对话: {txt[:30]}"):
            if product:
                allure.attach(
                    json.dumps(product, ensure_ascii=False, indent=2),
                    name=f"第 {i} 轮 - 商品信息",
                    attachment_type=allure.attachment_type.JSON
                )

            allure.attach(txt, name=f"第 {i} 轮 - 用户消息", attachment_type=allure.attachment_type.TEXT)

            # 调用聊天接口
            response = chat(txt, TOKEN, username, inquiry_product=product)
            result = response.json()

            # 基础断言
            assert result['code'] == 200, f"接口返回异常: {result['message']}"
            assert result['message'] == 'success'
            assert len(result['data']['ai_actions']) > 0, "AI 没有返回任何回复"

            # 提取并记录 AI 回复
            full_reply = extract_reply(result)
            assert len(full_reply) > 0, "AI 回复内容为空"
            allure.attach(full_reply, name=f"第 {i} 轮 - AI 回复", attachment_type=allure.attachment_type.TEXT)
            safe_print(f"AI: {full_reply}")

        # 等待 AI 回复落库后再发送下一条消息
        if i < len(messages):
            time.sleep(WAIT_AFTER_REPLY)


def get_random_product(token, shop_id="585"):
    """从店铺商品列表中随机选取一个商品"""
    response = get_products(token, shop_id, page=1, page_size=100)
    result = response.json()
    items = result.get('result', {}).get('data', [])
    if not items:
        return None
    item = random.choice(items)
    return {
        "id": str(item.get('product_id', '')),
        "title": item.get('product_title', ''),
        "url": f"https://item.taobao.com/item.htm?id={item.get('product_id', '')}"
    }


@allure.feature("商品问答")
@pytest.mark.parametrize("question", product_questions, ids=[f"Q{i+1}" for i in range(len(product_questions))])
def test_product_chat(question):
    """
    自动随机获取商品并提问测试：
    1. 从店铺商品列表中随机选取一个商品
    2. 用商品信息 + 问题发给 AI
    3. 验证 AI 能针对该商品给出回答

    每个问题都是独立的对话（不同 username），且随机选取不同商品
    """
    allure.dynamic.story(question)
    allure.dynamic.title(f"商品问答 - {question}")

    # Step 1: 随机获取商品
    with allure.step("随机获取商品"):
        product = get_random_product(TOKEN, shop_id="585")
        assert product is not None, "获取商品失败，请检查商品接口"
        allure.attach(
            json.dumps(product, ensure_ascii=False, indent=2),
            name="商品信息",
            attachment_type=allure.attachment_type.JSON
        )

    username = generate_username()
    allure.attach(username, name="用户名", attachment_type=allure.attachment_type.TEXT)

    # Step 2: 发送问题
    with allure.step(f"发送问题: {question}"):
        allure.attach(question, name="用户问题", attachment_type=allure.attachment_type.TEXT)
        response = chat(question, TOKEN, username, inquiry_product=product)
        result = response.json()

    # Step 3: 验证 AI 回复
    with allure.step("验证 AI 回复"):
        assert result['code'] == 200, f"接口返回异常: {result['message']}"
        assert result['message'] == 'success'
        assert len(result['data']['ai_actions']) > 0, "AI 没有返回任何回复"

        full_reply = extract_reply(result)
        assert len(full_reply) > 0, "AI 回复内容为空"
        allure.attach(full_reply, name="AI 回复", attachment_type=allure.attachment_type.TEXT)
        safe_print(f"AI: {full_reply}")


if __name__ == "__main__":
    # 支持直接运行: python test_chat.py
    # 只运行商品问答测试: python test_chat.py -k "test_product_chat"
    # --clean-alluredir: 每次运行前清理旧数据，报告只展示最新结果
    pytest.main([__file__, "-v", "-s", f"--alluredir={ALLURE_RESULTS_DIR}", "--clean-alluredir"])

    # 生成 Allure HTML 报告
    allure_report_dir = os.path.join(os.path.dirname(ALLURE_RESULTS_DIR), "allure-report")
    os.system(f'allure generate "{ALLURE_RESULTS_DIR}" -o "{allure_report_dir}" --clean')

    # 发送测试报告邮件
    from common.email_sender import send_test_report
    send_test_report(
        report_dir=allure_report_dir,
        recipients=["zhaowenlong@zhijianai.cn"]
    )