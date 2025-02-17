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
    line_bot_api.reply_message_with_http_info(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=message_text)]
        )
    )

with ApiClient(configuration) as api_client:

    """
    Handles the request when user want to add a new food data.
    prompting for user to input the subject of food they want to add
    """
    def addFoodAmountRequest(event):
        line_bot_api = MessagingApi(api_client)

        user_id = event.source.user_id
        reply_token = event.reply_token

        changeUserStatus(user_id, "addFoodAmount")
        sendReplyMessage(line_bot_api, reply_token, "請輸入欲新增的食物")

    """
    Handles the event when a user requests to add the amount of money for a food subject typed in previous subject.
    prompting for user to input the subject of food they want to add
    """
    def addFoodAmountMoneyRequest(event):
 
        line_bot_api = MessagingApi(api_client)
        user_id = event.source.user_id
        reply_token = event.reply_token
        receivedMessage = event.message.text

        updateTempData(user_id, receivedMessage)
        changeUserStatus(user_id, "addFoodAmountMoney")
        replyMessage = "請輸入" + receivedMessage + "的金額"
        sendReplyMessage(line_bot_api, reply_token, replyMessage)


    """
    Handles the event to confirm to add food data to database.
    Prompting a y/n message to let user to confirm to add food data to database.
    """
    def confirmAddFoodData(event):

        user_id = event.source.user_id
        passUserTypedAmountToConfirmMenu(user_id, event)
        
    """
    Adds food data to the database based on previous user typed.

    It then processes the data to extract the food name and amount, and inserts
    this information into the database. If the operation is successful, it sends
    a success message to the user. If there is an error, it sends a failure message.
    """
    def addFoodDataToDatabase(event):

        line_bot_api = MessagingApi(api_client)
        user_id = event.source.user_id
        reply_token = event.reply_token
        data = event.postback.data

        try:
            data = data.split()
            food = " ".join(data[:-1])
            foodAmount = float(data[-1])
            amount.insertFoodData(user_id, food, foodAmount)
            deleteTempData(user_id)
            changeUserStatus(user_id, "free")
            sendReplyMessage(line_bot_api, reply_token, "新增成功")
        except:
            sendReplyMessage(line_bot_api, reply_token, "新增失敗，請重新輸入")


