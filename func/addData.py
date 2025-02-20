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

    def addDataRequest(event):
        """
        Handle the request when user wants to add new data.

        Prompt for user to input the subject of they want to add.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, _ = extractEventVariables(event)

        sendReplyMessage(line_bot_api, reply_token, "請輸入欲新增的項目")
        changeUserStatus(user_id, "addDataSubject")


    def addDataMoneyRequest(event):
        """
        Handle the event when a user requests to add the amount of money for a subject typed in previous subject.

        Prompt for user to input the subject of they want to add.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, receivedMessage, _ = extractEventVariables(event)

        updateTempData(user_id, receivedMessage)
        replyMessage = "請輸入" + receivedMessage + "的金額"
        sendReplyMessage(line_bot_api, reply_token, replyMessage)
        changeUserStatus(user_id, "addDataMoney")


    def confirmAddData(event):
        """
        Handle the event to confirm to add data to database.

        Prompt a y/n message to let user confirm to add data to database.
        """
        user_id, reply_token, receivedMessage, _ = extractEventVariables(event)
        
        # Get amount subject from previous action
        subject = getTempData(user_id)
        # Get amount from user
        amount = receivedMessage

        # Get exchange rate
        exchangeRate = getExchangeRate(user_id)
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
        confirmAmount(subject, amount, prompt_message, reply_token, configuration)

    def addDataToDatabase(event):
        """
        Add data to the database based on previous user input.

        Process the data to extract the name and amount, and insert
        this information into the database. If the operation is successful, send
        a success message to the user. If there is an error, send a failure message.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, postback_data = extractEventVariables(event)

        try:
            data = postback_data.split()
            subject = " ".join(data[:-1])
            subjectAmount = float(data[-1])
            amount.insertData(subject, subjectAmount)
            deleteTempData(user_id)
            changeUserStatus(user_id, "free")
            sendReplyMessage(line_bot_api, reply_token, "新增成功")
        except:
            sendReplyMessage(line_bot_api, reply_token, "新增失敗，請重新輸入")


