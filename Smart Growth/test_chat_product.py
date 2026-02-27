import sys
import os
import yaml
import json
import time
import pytest
import allure
from api.chat import chat_with_product_id
from common.tool import get_token


def load_yaml_config():
    """加载商品测试专用的 yaml 配置"""
    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "test_chat_product.yaml")
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG = load_yaml_config()
ALLURE_RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "allure-results")
TOKEN = get_token()
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


class TestChatWithProduct:
    """商品咨询测试类"""

    @allure.feature("商品咨询")
    @allure.story("多轮对话")
    def test_multi_round_chat(self):
        """通过商品ID进行多轮对话测试"""
        username = generate_username()
        product_id = CONFIG.get('product_id')
        questions = CONFIG.get('test_questions', ['介绍一下这个商品'])

        allure.attach(username, name="用户名", attachment_type=allure.attachment_type.TEXT)
        allure.attach(product_id, name="商品ID", attachment_type=allure.attachment_type.TEXT)

        messages_history = []
        from api.product import get_product_by_id
        session_product = get_product_by_id(TOKEN, shop_id="585", product_id=product_id)
        if session_product:
            allure.attach(
                json.dumps(session_product, ensure_ascii=False, indent=2),
                name="会话商品信息",
                attachment_type=allure.attachment_type.JSON
            )
            print(f"\n[会话商品] {session_product['title']}\n")

        for i, txt in enumerate(questions, 1):
            with allure.step(f"第 {i} 轮对话: {txt[:30]}"):
                allure.attach(txt, name=f"第 {i} 轮 - 用户消息", attachment_type=allure.attachment_type.TEXT)

                now = int(time.time())
                user_msg = {
                    "role": "user",
                    "content": txt,
                    "created_at": now
                }
                messages_history.append(user_msg)

                from api.chat import chat
                response = chat(txt, TOKEN, username, inquiry_product=session_product, full_messages=messages_history)
                result = response.json()

                assert result['code'] == 200
                assert result['message'] == 'success'
                assert len(result['data']['ai_actions']) > 0

                full_reply = extract_reply(result)
                assert len(full_reply) > 0
                allure.attach(full_reply, name=f"第 {i} 轮 - AI回复", attachment_type=allure.attachment_type.TEXT)
                safe_print(f"Q{i}: {txt}")
                safe_print(f"A{i}: {full_reply}\n")

                now = int(time.time())
                for action in result['data']['ai_actions']:
                    if action.get('actionType') == 'sendMessage':
                        assistant_msg = {
                            "role": "assistant",
                            "content": action.get('payload', {}).get('content', ''),
                            "created_at": now
                        }
                        messages_history.append(assistant_msg)

            if i < len(questions):
                time.sleep(WAIT_AFTER_REPLY)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", f"--alluredir={ALLURE_RESULTS_DIR}", "--clean-alluredir"])

    allure_report_dir = os.path.join(os.path.dirname(ALLURE_RESULTS_DIR), "allure-report")
    os.system(f'allure generate "{ALLURE_RESULTS_DIR}" -o "{allure_report_dir}" --clean')

    from common.email_sender import send_test_report
    send_test_report(
        report_dir=allure_report_dir,
        recipients=["zhaowenlong@zhijianai.cn"]
    )
