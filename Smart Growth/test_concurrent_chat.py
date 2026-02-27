import sys
import os
import json
import time
import random
import yaml
import pytest
import allure
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.chat import chat
from api.product import get_product_by_index
from common.tool import get_token


def load_yaml_config():
    """读取并发对话测试配置"""
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "concurrent_chat.yaml"
    )
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# 加载配置
_config = load_yaml_config()
CONCURRENT_COUNT = _config['concurrent_config']['concurrent_count']
WAIT_BETWEEN_QUESTIONS = _config['concurrent_config']['wait_between_questions']
QUESTIONS = _config['conversations'][0]['questions']
SHOP_ID = _config['product_config']['shop_id']
PRODUCT_INDEX = _config['product_config']['product_index']


def generate_username():
    """生成 tb_时间戳 格式的用户名"""
    return f"tb_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"


def extract_reply(result):
    """从响应中提取 AI 回复内容"""
    replies = [
        action['payload']['content']
        for action in result['data']['ai_actions']
        if action.get('actionType') == 'sendMessage'
    ]
    return '\n\n'.join(replies)


def safe_print(text):
    """安全打印，处理 Windows 终端编码问题"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))


def run_single_conversation(conversation_id, token, product, questions):
    """
    运行单个对话

    参数:
        conversation_id: 对话ID
        token: 登录 token
        product: 商品信息
        questions: 问题列表

    返回:
        dict: 对话结果
    """
    username = generate_username()
    messages_history = []
    results = []

    start_time = time.time()

    try:
        for i, question in enumerate(questions, 1):
            # 构建用户消息
            now = int(time.time())
            user_msg = {
                "role": "user",
                "content": question,
                "created_at": now
            }
            messages_history.append(user_msg)

            # 调用聊天接口
            response = chat(
                question,
                token,
                username,
                inquiry_product=product,
                full_messages=messages_history,
                shop_id="585"
            )
            result = response.json()

            # 验证响应
            if result.get('code') != 200:
                return {
                    "conversation_id": conversation_id,
                    "success": False,
                    "error": f"接口返回异常: {result.get('message')}",
                    "duration": time.time() - start_time
                }

            if result.get('message') != 'success':
                return {
                    "conversation_id": conversation_id,
                    "success": False,
                    "error": f"接口返回 message 异常: {result.get('message')}",
                    "duration": time.time() - start_time
                }

            if len(result.get('data', {}).get('ai_actions', [])) == 0:
                return {
                    "conversation_id": conversation_id,
                    "success": False,
                    "error": "AI 没有返回任何回复",
                    "duration": time.time() - start_time
                }

            # 提取 AI 回复
            full_reply = extract_reply(result)
            if len(full_reply) == 0:
                return {
                    "conversation_id": conversation_id,
                    "success": False,
                    "error": "AI 回复内容为空",
                    "duration": time.time() - start_time
                }

            # 将 AI 的每条回复都添加到历史中
            now = int(time.time())
            for action in result['data']['ai_actions']:
                if action.get('actionType') == 'sendMessage':
                    assistant_msg = {
                        "role": "assistant",
                        "content": action.get('payload', {}).get('content', ''),
                        "created_at": now
                    }
                    messages_history.append(assistant_msg)

            results.append({
                "question": question,
                "reply": full_reply[:100] + "..." if len(full_reply) > 100 else full_reply
            })

            # 等待 AI 回复落库
            if i < len(questions):
                time.sleep(WAIT_BETWEEN_QUESTIONS)

        duration = time.time() - start_time
        return {
            "conversation_id": conversation_id,
            "success": True,
            "results": results,
            "duration": duration,
            "total_messages": len(messages_history)
        }

    except Exception as e:
        return {
            "conversation_id": conversation_id,
            "success": False,
            "error": str(e),
            "duration": time.time() - start_time
        }


@allure.feature("并发对话测试")
@allure.story("多并发对话稳定性测试")
def test_concurrent_conversations():
    """
    测试场景：同时运行多个对话，测试 AI 的稳定性
    并发数：从配置文件读取
    """
    allure.dynamic.title(f"并发对话稳定性测试 - {CONCURRENT_COUNT}个对话同时运行")

    print(f"\n{'='*80}")
    print(f"并发对话测试开始")
    print(f"并发数: {CONCURRENT_COUNT}")
    print(f"每轮问题数: {len(QUESTIONS)}")
    print(f"{'='*80}")

    # 获取 token 和商品
    token = get_token()
    product = get_product_by_index(token, shop_id=SHOP_ID, index=PRODUCT_INDEX)
    assert product is not None, "获取商品失败"

    allure.attach(
        json.dumps(product, ensure_ascii=False, indent=2),
        name="测试商品信息",
        attachment_type=allure.attachment_type.JSON
    )

    print(f"\n[测试商品] {product['title']}")

    # 并发运行对话
    all_results = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=CONCURRENT_COUNT) as executor:
        # 提交所有任务
        futures = {
            executor.submit(
                run_single_conversation,
                i,
                token,
                product,
                QUESTIONS
            ): i
            for i in range(CONCURRENT_COUNT)
        }

        # 收集结果
        for future in as_completed(futures):
            result = future.result()
            all_results.append(result)

            conversation_id = result['conversation_id']
            if result['success']:
                print(f"\n[对话 {conversation_id}] 成功! 耗时: {result['duration']:.2f}s, 消息数: {result['total_messages']}")
                for j, r in enumerate(result['results'], 1):
                    print(f"  [{j}] Q: {r['question'][:30]}... -> A: {r['reply'][:50]}...")
            else:
                print(f"\n[对话 {conversation_id}] 失败! 错误: {result['error']}")

    total_duration = time.time() - start_time

    # 统计结果
    success_count = sum(1 for r in all_results if r['success'])
    fail_count = sum(1 for r in all_results if not r['success'])

    print(f"\n{'='*80}")
    print(f"测试完成!")
    print(f"总耗时: {total_duration:.2f}s")
    print(f"成功: {success_count}/{CONCURRENT_COUNT}")
    print(f"失败: {fail_count}/{CONCURRENT_COUNT}")
    print(f"{'='*80}")

    # 附加结果到 Allure
    allure.attach(
        json.dumps(all_results, ensure_ascii=False, indent=2),
        name="所有对话结果",
        attachment_type=allure.attachment_type.JSON
    )

    # 断言所有对话都成功
    assert fail_count == 0, f"有 {fail_count} 个对话失败"
    assert success_count == CONCURRENT_COUNT, f"只有 {success_count}/{CONCURRENT_COUNT} 个对话成功"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
