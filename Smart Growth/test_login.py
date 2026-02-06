import pytest
from api.login import login


class TestLogin:

    def test_login_success(self):
        """测试登录成功并获取 token"""
        response = login("测试专用1", "init@9934")
        result = response.json()

        assert result['code'] == 200
        assert result['message'] == '登录成功'
        assert 'accessToken' in result['data']

        token = result['data']['accessToken']
        print(f"\n登录成功，accessToken: {token[:50]}...")
        print(f"expiresIn: {result['data']['expiresIn']}s")

    def test_login_wrong_password(self):
        """测试密码错误"""
        response = login("测试专用1", "wrong_password")
        result = response.json()

        assert result['code'] != 200
        print(f"\n密码错误，返回: {result['message']}")

    def test_login_empty_account(self):
        """测试空账号"""
        response = login("", "init@9934")
        result = response.json()

        assert result['code'] != 200
        print(f"\n空账号，返回: {result['message']}")
