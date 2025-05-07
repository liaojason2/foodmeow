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

from func import addData, amount, menu, user, addData
from func.utils import convertAmountToCent, convertCentToDecimalString

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

        elif (user.checkUserStatus(userId) == "addDataSubject"):
            '''
            Add amount step 3
            
            Receive user-typed subject and prompt for user to input the amount of money.
            '''
            addData.addDataSubjectRequest(event)

        elif (user.checkUserStatus(userId) == "addDataMoney"):
            '''
            Add amount step 4

            Receive user-typed amount and prompt for user to confirm the amount.
            '''
            addData.addDataMoneyRequest(event)

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
        

        # Add data
        elif (postbackData[:7] =="addData"):
            '''
            Add data step 1

            User request to add data.
            
            Receive Postback event "addData" or with category name after space like "addData food".

            if {category} is not include in postback message, it will prompt the category menu for user to select category.
            if {category} include in postback message, it will skip category menu and prompt for user to input the subject of data they want to add.
            - include category message might come from user want to add data when was added a data.
            '''

            if len(postbackData.split(" ")) > 1:
                event.postback.data = postbackData.split(" ")[1]
                addData.addDataCategoryRequest(event)
                return
            
            addData.selectDataCategoryRequest(event)

        elif (user.checkUserStatus(userId) == "addDataCategory"):
            '''
            Add amount step 2

            User was selected category and prompt for user to input the subject of data they want to add.

            Receive Postback event "addDataCategory"

            '''
            addData.addDataCategoryRequest(event)

        elif user.checkUserStatus(userId) == "addDataMoney" and postbackData == "Yes":
            '''
            Add amount step 5

            Add data to the database based on previous user input.

            Receive Postback event "addDataMoney"
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

        elif (user.checkUserStatus(userId) == "giveAmount"):
            total = event.postback.data
            print("total", total)
            # TODO: customize the amount, checkout to cent 
            total = convertAmountToCent(total) // 100 * 100

            replyMessage = f"結帳完成，總金額為 {convertCentToDecimalString(total)} 元"

            amount.giveAmount(total)
            user.changeUserStatus(userId, "free")
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=replyToken,
                    messages=[TextMessage(text=replyMessage)]
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
