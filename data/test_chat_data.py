import os
import yaml


def load_yaml(filename):
    """读取 data 目录下的 YAML 文件"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# 读取 YAML 数据
_raw = load_yaml("chat_data.yaml")

# 多轮对话测试数据
# 格式: [(session_name, messages), ...]
test_chat_sessions = [(item['session'], item['messages']) for item in _raw['chat_sessions']]

# 商品问答测试数据
# 格式: ["问题1", "问题2", ...]
product_questions = _raw['product_questions']