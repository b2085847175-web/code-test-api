
from requests import session
import BASE_URL


def org(description,is_enabled,name,owner_id,owner_name,token):
        url = BASE_URL.BASE_URL + '/orgs'
        data = {'description':description,'is_enabled':is_enabled,'name':name,'owner_id':owner_id,'owner_name':owner_name}
        result =  session().post(url=url,data=data,headers = token)
        return result


