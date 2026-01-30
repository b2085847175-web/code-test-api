import requests
import pytest
from api.chat import chat
from data.test_chat_data import test_chat_data

@pytest.mark.parametrize("txt",test_chat_data)
def test_chat(txt):
    result = chat(txt).json()
    replies = [
        action['payload']['content']
        for action in result['data']['ai_actions']
        if action.get('actionType') == 'sendMessage'
    ]
    full_reply = '\n\n'.join(replies)
    print(full_reply)

    # print(result.json()['data']['ai_actions'][0]['payload']['content'])
    # print(result.json())


if __name__ == '__main__':
    test_chat()