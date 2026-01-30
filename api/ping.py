##示例代码
import requests
from requests import session

import BASE_URL
def ping():
    url = BASE_URL.BASE_URL + '/system/ping'
    return session().get(url)

