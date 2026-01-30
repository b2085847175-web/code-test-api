from requests import session
import BASE_URL

def creat_user(company_role_name,name,password,phone,type,header):
    url = BASE_URL.BASE_URL + "/users"
    data = {'company_role_name':company_role_name,'name':name,'password':password,'phone':phone,'type':type}
    result = session().post(url = url,data = data,headers = header)
    return result