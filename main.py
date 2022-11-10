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
from func import user

import math

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
    app.logger.info("Request body: " + body)

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

    # Add food amount step 2
    elif(user.checkUserStatus(userId) == "AddFoodAmount"):
        user.updateTempData(userId, event.message.text)
        user.changeUserStatus(userId, "AddFoodAmountMoney")
        message = "請輸入" + event.message.text + "的金額"
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message)
        )

    # Add food amount step 3 (comfirm food amount correct)
    elif(user.checkUserStatus(userId) == "AddFoodAmountMoney"):
        subject = user.getTempData(userId)
        amount = event.message.text
        prompt_message = '請確認是否要將 ' + amount + " 的 " + subject + "加入資料庫中"
        reply_token = event.reply_token
        menu.confirm(subject, amount, prompt_message, reply_token)

    # Add amount
    elif(user.checkUserStatus(userId) == "AddAmount"):
        user.updateTempData(userId, event.message.text)
        user.changeUserStatus(userId, "AddAmountMoney")
        message = "請輸入" + event.message.text + "的金額"
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message)
        )

    elif(user.checkUserStatus(userId) == "AddAmountMoney"):
        subject = user.getTempData(userId)
        amount = event.message.text
        prompt_message = '請確認是否要將 ' + amount + " 的 " + subject + "加入資料庫中"
        reply_token = event.reply_token
        menu.confirm(subject, amount, prompt_message, reply_token)




@ handler.add(PostbackEvent)
def postback_message(event, PostbackMessage):
    userId = event.source.user_id

    # Force Quit (if anything wrong)
    if(event.postback.data == "forceQuit"):
        user.clearDataToDefault(userId)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text = "您已退出操作，請重新開始")
        )

    # Open Amount Menu
    if(event.postback.data == "Amount"):
        menu.amountMenu(event)

    # Add Food Amount Step 1
    elif(event.postback.data == "addFoodAmount"):
        user.changeUserStatus(userId, "AddFoodAmount")
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text = "請輸入食物")
        )

    # Add Food Amount to database
    elif(user.checkUserStatus(userId) == "AddFoodAmountMoney"):
        try:
            data = event.postback.data
            data = data.split()
            food = ""
            for i in range(0, len(data)-1):
                food += data[i]
            foodAmount = float(data[-1])

            amount.insertFoodData(userId, food, foodAmount)
            user.deleteTempData(userId)
            user.changeUserStatus(userId, "free")
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text = "新增成功")
            )
        except TypeError:
            user.clearDataToDefault(userId)
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text = "輸入格式有誤，請重新操作")
            )

    # Add Amount Step 1
    elif(event.postback.data == "addAmount"):
        user.changeUserStatus(userId, "AddAmount")
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text = "請輸入項目")
        )

    # Add Amount to database
    if(user.checkUserStatus(userId) == "AddAmountMoney"):
        data = event.postback.data
        data = data.split()
        subject = ""
        for i in range(0, len(data)-1):
            subject += data[i]
        subjectAmount = float(data[-1])
        amount.insertData(subject, subjectAmount)
        user.deleteTempData(userId)
        user.changeUserStatus(userId, "free")
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text = "新增成功")
        )
    
    # Get total amount expect already checkout
    if(event.postback.data == "totalAmount"):
        total = amount.getTotalAmount()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text = total)
        ) 
    

    if(event.postback.data == "giveAmount"):
        user.changeUserStatus(userId, "giveAmount")
        menu.giveAmountConfirm(event)
    
    if(user.checkUserStatus(userId) == "giveAmount"):
        total = event.postback.data
        total = math.floor(float(total))
        amount.giveAmount(float(total))
        user.changeUserStatus(userId, "free")
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text = "已完成結帳，金額 " + str(total) + " 元")
        )

    if(event.postback.data == "getHistoryAmount"):
        history = amount.getHistory()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text = history)
        )

if __name__ == "__main__":
    app.run()

