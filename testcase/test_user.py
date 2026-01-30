from tabnanny import check

import pytest
from api.api_company.users import creat_user
from api.api_company.login import login
from api.api_company.org import org
from data.test_user_data import test_user
from data.test_user_data import test_org
import pytest_check as check

# 获取信息头
header = login("13000000003","Ww12345678..").json()['data']['access_token']
headers = {"Authorization": f"Bearer {header}"}

@pytest.mark.parametrize("role, username, password, phone, org_id",test_user)
def test_user(role, username, password, phone, org_id):
    result = creat_user(role, username, password, phone, org_id,headers)

@pytest.mark.skip
@pytest.mark.parametrize("description,is_enabled,name,owner_id,owner_name",test_org)
def test_org(description,is_enabled,name,owner_id,owner_name):
    result = org(description,is_enabled,name,owner_id,owner_name,headers)
    print(result.json())

if __name__ == "__main__":
    test_user()
    test_org()