from requests import session


def chat(txt):
    url = "https://console.zhiyan.chat/chat/answer"
    body = {
  "platform": "tmall",
  "shop_name": "儒意化妆品旗舰店",
  "account": "测试专用1",
  "username": "tb_1768997975328",
  "shop_id": "1",
  "is_test": "ture",
  "last_order_time": 1768997977,
  "last_order_info": None,
  "request_id": "aa2090d0-2fe2-47a9-9afb-8213feb25036",
  "inquiry_product": {},
  "messages": [
    {
      "role": "user",
      "content": txt,
      "created_at": 1768997977
    }
  ]
}
    token = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Nywicm9sZSI6InN1cGVyYWRtaW4iLCJ1c2VybmFtZSI6IuadjuW4hSIsImNvbXBhbnlfaWQiOjEsImlhdCI6MTc2ODk5NzQxNiwiZXhwIjoxNzY5MDgzODE2fQ.HiZ6IYbQnC6Hp7ynZxo1sDqoP4JFVHrx8rhFxQPsXDc", "Content-Type": "application/json"}
    return session().post(url=url,json=body,headers=token)

    # {'type': 'chat_response', 'code': 200, 'message': 'success', 'data': {'username': 'tb_1768997975328',
    #                                                                       'ai_actions': [{'actionType': 'sendMessage',
    #                                                                                       'payload': {
    #                                                                                           'contentType': 'text',
    #                                                                                           'content': '您好！有什么可以帮您的吗~'}}],
    #                                                                       'system_actions': [],
    #                                                                       'last_msg_time': 1768997977},
    #  'request_id': 'aa2090d0-2fe2-47a9-9afb-8213feb25036'}

