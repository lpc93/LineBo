import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
from pygooglenews import GoogleNews
from datetime import datetime
from dotenv import load_dotenv
import requests

# 加載環境變數
load_dotenv()

app = Flask(__name__)
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def get_weather(city_name):
    gn = GoogleNews(lang='zh-TW', country='TW')
    search = gn.search(f"{city_name} 天氣")
    if search['entries']:
        entry = search['entries'][0]
        title = entry.get('title', '無法取得天氣資訊')
        link = entry.get('link', '無法取得天氣資訊')
        return f"{title}\n更多資訊: {link}"
    else:
        return "無法取得天氣資訊，請檢查城市名稱是否正確。"

def get_news(keyword):
    gn = GoogleNews(lang='zh-TW', country='TW')
    search = gn.search(keyword)
    if search['entries']:
        entries = search['entries'][:3]  # 取前3條新聞
        news = "\n\n".join([f"{entry.get('title', '無標題')}\n{entry.get('link', '無鏈接')}" for entry in entries])
        return news
    else:
        return "無法取得新聞資訊，請檢查關鍵詞是否正確。"

def get_local_time(city_name):
    try:
        response = requests.get(f"http://worldtimeapi.org/api/timezone/{city_name}")
        data = response.json()
        if response.status_code == 200:
            local_time = data['datetime']
            return f"{city_name} 的當地時間是 {local_time}"
        else:
            return "無法取得當地時間，請檢查城市名稱是否正確。"
    except:
        return "無法取得當地時間，請檢查城市名稱是否正確。"

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if msg.startswith("天氣"):
        city_name = msg.split("天氣", 1)[1].strip()
        if city_name:
            weather_info = get_weather(city_name)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=weather_info))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請提供城市名稱，例如：天氣 台北"))
    elif msg.startswith("新聞"):
        keyword = msg.split("新聞", 1)[1].strip()
        if keyword:
            news_info = get_news(keyword)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=news_info))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請提供新聞關鍵詞，例如：新聞 科技"))
    elif msg.startswith("時間"):
        city_name = msg.split("時間", 1)[1].strip()
        if city_name:
            time_info = get_local_time(city_name)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=time_info))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請提供城市名稱，例如：時間 台北"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)

@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name} 歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

