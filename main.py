#!/usr/bin/env python

import os
import math
from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    PostbackEvent,
)
from func import addData, amount, menu, user, addFoodAmount, addData

load_dotenv()

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('CHANNEL_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))


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
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


def passUserTypedAmountToConfirmMenu(userId, event):
    receivedMessage = event.message.text
    replyToken = event.reply_token

    # Get amount subject from previous action
    subject = user.getTempData(userId)
    # Get amount from user
    amount = receivedMessage
    # Get exchange rate
    exchangeRate = user.getExchangeRate(userId)
    # Count exchange rate and convert to integer
    amount = int(float(amount) * float(exchangeRate))
    # Covert to string for showing prompt_message
    amount = str(amount)
    # Define prompt_message to confirm section
    prompt_message = '請確認是否要將 ' + amount + " 的 " + subject + "加入資料庫中"
    if (exchangeRate != 1.0):
        prompt_message = '請確認是否要將 ' + amount + " 的 " + \
            subject + " 加入資料庫中（匯率 " + str(exchangeRate) + "）。"
    # Pass to confirmAmount section
    menu.confirmAmount(subject, amount, prompt_message,
                       replyToken)


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        userId = event.source.user_id
        profile = line_bot_api.get_profile(userId)
        reply_token = event.reply_token
        receivedMessage = event.message.text

        if user.checkUserExist(profile) == "NewUser":
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text="歡迎使用本程式")]
                )
            )

        elif (receivedMessage == "開啟選單"):
            menu.welcomeMenu(event, configuration)

        # Add food amount
        # elif (user.checkUserStatus(userId) == "addFoodAmount"):
        #     '''
        #     Add food amount step 2

        #     Receive user-typed food subject and prompt for user to input the amount of money.
        #     '''
        #     addFoodAmount.addFoodAmountMoneyRequest(event)

        # elif (user.checkUserStatus(userId) == "addFoodAmountMoney"):
        #     '''
        #     Add food amount step 3

        #     Receive user-typed amount and prompt for user to confirm the amount.
            # '''
            # addFoodAmount.confirmAddFoodData(event)

        # Add amount
        elif (user.checkUserStatus(userId) == "addDataCategory"):
            addData.selectDataCategory(event)

        elif (user.checkUserStatus(userId) == "addDataSubject"):
            addData.addDataSubjectRequest(event)

        elif (user.checkUserStatus(userId) == "addDataMoney"):
            '''
            '''
            addData.addDataMoneyRequest(event)

        # elif (user.checkUserStatus(userId) == "addDataMoney"):
        #     '''
        #     Add amount step 4

        #     Receive user-typed amount and prompt for user to confirm the amount.
        #     '''
        #     addData.confirmAddData(event)

        # User request to change exchange rate
        elif (user.checkUserStatus(userId) == "updateExchangeRate"):
            exchangeRate = receivedMessage
            prompt_message = '請確認匯價為 ' + exchangeRate
            user.changeUserStatus(userId, "updateExchangeRateConfirm")
            menu.confirmChangeExchangeRate(
                exchangeRate, prompt_message, reply_token, configuration)


@handler.add(PostbackEvent)
def handle_postback_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        userId = event.source.user_id
        replyToken = event.reply_token
        postbackData = event.postback.data

        # Force Quit (if anything wrong)
        if (postbackData == "forceQuit"):
            user.clearDataToDefault(userId)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=replyToken,
                    messages=[TextMessage(text="您已退出操作，請重新開始")]
                )
            )

        # Open Amount Menu
        if (postbackData == "Amount"):
            menu.amountMenu(event)

        # Add food amount
        elif (postbackData == "addFoodAmount"):
            '''
            Add food amount step 1

            Receive Postback event "addFoodAmount"
            
            Prompt for user to input the subject of food they want to add.
            '''
            addFoodAmount.addFoodAmountRequest(event)

     
        # elif (user.checkUserStatus(userId) == "addFoodAmountMoney"):
        #     '''
        #     Add food amount step 4

        #     Receive Postback event "addFoodAmountMoney"
            
        #     Handle the event to confirm to add food data to database.
        #     '''
        #     addFoodAmount.addFoodDataToDatabase(event)
        

        # Add amount
        elif (postbackData == "addData"):
            '''
            Add amount step 1
            
            Receive Postback event "addData"
            '''
            addData.selectDataCategoryRequest(event)

        if (user.checkUserStatus(userId) == "addDataCategory"):
            '''
            Add amount step 2

            Receive Postback event "addDataCategory"

            Prompt for user to input the subject of data they want to add.
            '''
            addData.addDataCategoryRequest(event)

        if user.checkUserStatus(userId) == "addDataMoney" and postbackData == "Yes":
            '''
            Add amount step 5

            Receive Postback event "addDataMoney"

            Add data to the database based on previous user input.
            '''
            addData.addDataToDatabase(event)

        # Get total amount expect already checkout
        if (postbackData == "totalAmount"):
            total = amount.getTotalAmount()
            total = str(total)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=replyToken,
                    messages=[TextMessage(text=total)]
                )
            )

        # Give amount confirm
        if (postbackData == "giveAmount"):
            user.changeUserStatus(userId, "giveAmount")
            menu.giveAmountConfirm(event, configuration)

        if (user.checkUserStatus(userId) == "giveAmount"):
            total = event.postback.data
            total = math.floor(float(total))
            amount.giveAmount(float(total))
            user.changeUserStatus(userId, "free")
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=replyToken,
                    messages=[TextMessage(
                        text="已完成結帳，金額 " + str(total) + " 元")]
                )
            )

        if (postbackData == "getHistoryAmount"):
            history = amount.getHistory()
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=replyToken,
                    messages=[TextMessage(text=history)]
                )
            )

        # User request to change exchange rate
        if (postbackData == "updateExchangeRate"):
            user.changeUserStatus(userId, "updateExchangeRate")
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=replyToken,
                    messages=[TextMessage(text="請輸入匯價")]
                )
            )

        if (user.checkUserStatus(userId) == "updateExchangeRateConfirm"):
            exchangeRate = float(postbackData)
            user.updateExchangeRate(userId, exchangeRate)
            user.changeUserStatus(userId, "free")
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=replyToken,
                    messages=[TextMessage(text="變更成功")]
                )
            )


if __name__ == "__main__":
    app.run()
