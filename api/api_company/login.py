import BASE_URL
from requests import session



def login(phone,password):
    url = BASE_URL.BASE_URL + "/auth/login"
    data = {"phone":phone,"password":password}
    result = session().post(data = data,url=url)
    return result
