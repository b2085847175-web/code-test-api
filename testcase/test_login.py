from api.api_company.login import login
import pytest_check as check

def test_login():
    phone = "13000000003"
    password = "Ww12345678.."
    result = login(phone,password)
    # {'code': 200, 'data': {
    #     'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NDEzLCJjb21wYW55X2lkIjoxLCJjb21wYW55X3JvbGVfaWQiOjIsImlhdCI6MTc2ODkxMTk4MSwiZXhwIjoxNzY4OTk4MzgxfQ.MK_O0y6IEYkg1dlMcTE4JEeNA6nj8TX01qlzdMvVgtg',
    #     'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NDEzLCJjb21wYW55X2lkIjoxLCJjb21wYW55X3JvbGVfaWQiOjIsImlhdCI6MTc2ODkxMTk4MSwiZXhwIjoxNzY5NTE2NzgxfQ.55ICWnE-GBW542gSpIUb3wy3kv4OYEWdsiIoSrbbY-4',
    #     'expires_in': 3600, 'id': 413, 'name': '管理员', 'type': 1, 'company_role_id': 2, 'company_role_name': '管理员',
    #     'company_id': 1, 'company_name': '默认公司'}, 'message': '登录成功', 'timestamp': 1768911982}
    check.equal(result.status_code,200,"状态码不是200")
    check.equal(result.json()['code'],200,"code不是200")
    check.not_equal(result.json()['data']['access_token'],"token不为空")
    # print(result.json())




if __name__ == "__main__":
    test_login()