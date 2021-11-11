#!/usr/bin/env python

import os
from dotenv import load_dotenv
from flask import Flask, request, abort
from func import menu, user
from linebot.models import (
    MessageEvent, TextMessage,  TextSendMessage,
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models.events import PostbackEvent

from func import menu, amount

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

    if user.checkUserExist(profile) == "NewUser":
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="歡迎使用本程式"))

    elif(event.message.text == "開啟選單"):
        menu.welcomeMenu(event)

    elif(user.checkUserStatus(userId) == "AddFoodAmount"):
        user.updateTempData(userId, event.message.text)
        user.changeUserStatus(userId, "AddFoodAmountMoney")
        message = "請輸入" + event.message.text + "的金額"
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message)
        )

    elif(user.checkUserStatus(userId) == "AddFoodAmountMoney"):
        menu.confirm(event)




@ handler.add(PostbackEvent)
def postback_message(event, PostbackMessage):
    userId = event.source.user_id

    if (event.postback.data == "Amount"):
        menu.amountMenu(event)

    if(event.postback.data == "AddFoodAmount"):
        user.changeUserStatus(userId, "AddFoodAmount")
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text = "請輸入食物")
        )
    
    if(user.checkUserStatus(userId) == "AddFoodAmountMoney"):
        data = event.postback.data
        data = data.split()
        food = data[0]
        foodAmount = int(data[1])
        amount.insertFoodData(food, foodAmount)
        user.deleteTempData(userId)
        user.changeUserStatus(userId, "free")
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text = "新增成功")
        )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
