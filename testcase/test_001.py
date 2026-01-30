import requests
import pytest_check as check
from api.ping import ping


def test_ping():
    data = ping()

    # 结果
    # {'code': 200, 'data': 'Pong', 'message': 'Success', 'timestamp': 1768909502}
    check.equal(data.status_code, 200, "code 不是 200")
    check.equal(data.json()['code'], 200, "code 值不是 200")
    check.equal(data.json()['message'], 'Success', "message 值不是 Success")
    check.equal(data.json()['data'], 'Pong', "data 值不是 Pong")
    # print(data.json())


if __name__ == "__main__":
    test_ping()