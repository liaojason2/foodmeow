import os
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3 import (
    WebhookHandler
)

from .user import (
    changeUserStatus, updateTempData, getTempData, getExchangeRate, deleteTempData
)
from .menu import confirmAmount
from . import amount

load_dotenv()

configuration = Configuration(access_token=os.getenv('CHANNEL_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

def passUserTypedAmountToConfirmMenu(userId, event):
    """Pass user-typed amount to confirm menu."""
    receivedMessage = event.message.text
    replyToken = event.reply_token

    # Get amount subject from previous action
    subject = getTempData(userId)
    # Get amount from user
    amount = receivedMessage
    # Get exchange rate
    exchangeRate = getExchangeRate(userId)
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
    confirmAmount(subject, amount, prompt_message, replyToken, configuration)

def sendReplyMessage(line_bot_api, reply_token, message_text):
    """Send a reply message."""
    line_bot_api.reply_message_with_http_info(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=message_text)]
        )
    )

with ApiClient(configuration) as api_client:

    def extractEventVariables(event):
        """Extract variables from the event."""
        user_id = event.source.user_id
        reply_token = event.reply_token
        message_text = event.message.text if hasattr(event, 'message') else None
        postback_data = event.postback.data if hasattr(event, 'postback') else None
        return user_id, reply_token, message_text, postback_data

    def addFoodAmountRequest(event):
        """
        Handle the request when user wants to add new food data.

        Prompt for user to input the subject of food they want to add.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, _ = extractEventVariables(event)

        tempData = {
            "category": "food"
        }

        updateTempData(user_id, tempData)        
        sendReplyMessage(line_bot_api, reply_token, "請輸入欲新增的食物")
        changeUserStatus(user_id, "addDataSubject")
'''
    def addFoodAmountMoneyRequest(event):
        """
        Handle the event when a user requests to add the amount of money for a food subject typed in previous subject.

        Prompt for user to input the subject of food they want to add.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, receivedMessage, _ = extractEventVariables(event)

        updateTempData(user_id, receivedMessage)
        changeUserStatus(user_id, "addFoodAmountMoney")
        replyMessage = "請輸入" + receivedMessage + "的金額"
        sendReplyMessage(line_bot_api, reply_token, replyMessage)

    def confirmAddFoodData(event):
        """
        Handle the event to confirm to add food data to database.

        Prompt a y/n message to let user confirm to add food data to database.
        """
        user_id, _, _, _ = extractEventVariables(event)
        passUserTypedAmountToConfirmMenu(user_id, event)

    def addFoodDataToDatabase(event):
        """
        Add food data to the database based on previous user input.

        Postback data: <food name> <amount>
        Postback data example: "apple juice 100"

        Process the data to extract the food name and amount, and insert
        this information into the database. If the operation is successful, send
        a success message to the user. If there is an error, send a failure message.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, postback_data = extractEventVariables(event)

        try:
            data = postback_data.split()
            food = " ".join(data[:-1])
            foodAmount = float(data[-1])
            amount.insertFoodData(user_id, food, foodAmount)
            deleteTempData(user_id)
            changeUserStatus(user_id, "free")
            sendReplyMessage(line_bot_api, reply_token, "新增成功")
        except:
            sendReplyMessage(line_bot_api, reply_token, "新增失敗，請重新輸入")
'''

