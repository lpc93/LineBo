from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetimefrom flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

import tempfile
import os
import datetime
import time
import traceback

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Channel Access Token
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
# Channel Secret
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

# 確保環境變數已設置
if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    raise EnvironmentError("Please set the CHANNEL_ACCESS_TOKEN and CHANNEL_SECRET environment variables.")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Check your channel access token/channel secret.")
        abort(400)
    return 'OK'

def get_response_message(msg):
    questions_answers = {
        "apple": "蘋果",
        "banana": "香蕉",
        "cat": "貓",
        "dog": "狗",
        "elephant": "大象",
        "flower": "花",
        "guitar": "吉他",
        "house": "房子",
        "ice": "冰",
        "tiger": "虎",
        "jacket": "夾克",
        "keyboard": "鍵盤",
        "lemon": "檸檬",
        "monkey": "猴子",
        "notebook": "筆記本",
        "orange": "橙子",
        "piano": "鋼琴",
        "queen": "女王",
        "rabbit": "兔子",
        "sun": "太陽",
        "tree": "樹",
        "umbrella": "雨傘",
        "violin": "小提琴",
        "whale": "鯨魚",
        "xylophone": "木琴",
        "yacht": "遊艇",
        "zebra": "斑馬",
        "bread": "麵包",
        "car": "車",
        "duck": "鴨子",
        "你最近的感覺如何？": "我大多數時候感到焦慮和壓力很大。",
        "你能描述一下你目前的心情嗎？": "我經常感到悲傷和沮喪。",
        "你最近經歷過什麼重大生活變化嗎？": "是的，我最近搬到了一個新城市工作。",
        "你通常如何應對壓力？": "我通常會試圖通過愛好或鍛煉來分散注意力，但這並不總是有效。",
        "你有可以依靠的支持系統嗎？": "我有幾個可以談心的親密朋友和家人。",
        "你喜歡做哪些活動？": "我喜歡閱讀、遠足和畫畫。",
        "你有注意到你的睡眠模式有變化嗎？": "是的，我最近一直很難入睡和保持睡眠。",
        "你對這次心理輔導有什麼目標？": "我希望學會更好地管理壓力，並提高我的整體幸福感。",
        "還有什麼你認為我應該知道的嗎？": "我有時覺得自己不夠好，這影響了我的自信心。"
    }
    return questions_answers.get(msg, msg)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    response = get_response_message(msg)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(response))

@handler.add(PostbackEvent)
def handle_postback(event):
    app.logger.info(f"Received postback data: {event.postback.data}")

@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name} 歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

