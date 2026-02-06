import os
import yaml


def load_yaml(filename):
    """读取 data 目录下的 YAML 文件"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# 读取 YAML 数据，转为 pytest 参数化格式
# 每个 session 代表一个用户的多轮对话
# 格式: [(session_name, messages), ...]
# messages: [{"txt": "...", "keywords": [...]}, ...]
_raw = load_yaml("chat_data.yaml")
test_chat_sessions = [(item['session'], item['messages']) for item in _raw]