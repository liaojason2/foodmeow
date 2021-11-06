#!/usr/bin/env python

import os
from dotenv import load_dotenv
from flask import Flask, request, abort
from func import welcome, user
from linebot.models import (
    MessageEvent, TextMessage,  TextSendMessage,
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models.events import Postback, PostbackEvent

load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("CHANNEL_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent)
def handle_text_message(event, TextMessage):
    userId = event.source.user_id
    profile = line_bot_api.get_profile(userId)

    if(event.message.text == "test"):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="test"))

    if user.checkUserExist(profile) == "NewUser":
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="歡迎使用本程式"))

    if(event.message.text == "選單"):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="test"))
    
    if(event.message.text == "開啟選單"):
        welcome.welcomeMenu(event)

@handler.add(PostbackEvent)
def test(event, PostbackMessage):

    if (event.postback.data == "add"):
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="success"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))