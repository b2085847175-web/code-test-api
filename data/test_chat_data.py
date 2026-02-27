import os
import yaml


def load_yaml(filename):
    """读取 data 目录下的 YAML 文件"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_raw = load_yaml("chat_data.yaml")
test_questions = _raw.get('test_questions', [])
