import os
import random
import re
import string

import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

TITLE_REGEX = re.compile(r"\*\*\[(.*)\]\(<(.*)>\)\*\*")

class Message(BaseModel):
    content: str
    username: str
    avatar_url: str
    tts: bool


load_dotenv()

if os.getenv('TOKEN') is None:
    token = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(68))
    os.environ['TOKEN'] = token

    print(f"Generated new token: {token}")

app = FastAPI()

@app.get('/')
def get_webhook():
    return {
        "type": 1,
        "id": "1084689733986291794",
        "name": "Discord - Channel.io Webhook Bridge",
        "avatar": None,
        "channel_id": "632245120456196104",
        "guild_id": "494512629696561154",
        "application_id": None,
        "token": os.getenv('TOKEN')
    }

# {
#   'content': '**[LLM에 Stable Diffusion Moment가 오고 있다](<https://news.hada.io/topic?id=8684&utm_source=discord&utm_medium=bot&utm_campaign=995>)**\r\n
#               - 2022년 8월의 Stable Diffuion(SD) 공개는 중요한 순간이었고, 이로 인해 폭발적인 혁신이 지금까지도 진행되고 있음  \r\n
#               - 최근에는 ControlNet이 기능면에서 MidJourney 와 DALL-E를 뛰어넘음   \r\n
#               - SD의 공개는 생성형 AI에 대한 새로운 관심을 만들어냈고, 11월의 ChatGPT 출시로 인해 그 웨이브가 더 거세짐   \r\n
#               -...', 
#   'username': 'GeekNews', 
#   'avatar_url': 'https://social.news.hada.io/geeknews.png', 
#   'tts': False 
# }
@app.post('/')
async def post_webhook(message: Message):
    content = message.content.split('\r\n')

    match = TITLE_REGEX.match(content[0])

    description = [{'type': 'text', 'value': line.strip()[2:] if line.strip()[0] == '-' else line.strip()} for line in content[1:]]

    data = {
        "blocks": [
            {
                "type": "text",
                "value": f'<b><link type="url" value="{match[2]}">{match[1]}</link></b>'
            },
            {
                "type": "bullets",
                "blocks": description
            }
        ],
        "options": ["actAsManager", "immutable"]
    }

    print(data)

    result = requests.post(f"https://api.channel.io/open/v5/groups/{os.environ['GROUP_ID']}/messages", json=data, headers={
        "Accept": "application/json",
        "x-access-key": os.environ['CHANNEL_ACCESS_KEY'],
        "x-access-secret": os.environ['CHANNEL_ACCESS_SECRET']
    })

    print(result.content)