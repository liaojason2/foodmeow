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
from .menu import selectDataCategory, confirmAmount, addDataSuccess
from . import amount
from .amount import insertData
from .config import getFoodMultiple

load_dotenv()

configuration = Configuration(access_token=os.getenv('CHANNEL_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

def sendReplyMessage(line_bot_api, reply_token, message_text):
    """Send a reply message."""
    line_bot_api.reply_message_with_http_info(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=message_text)]
        )
    )

def convertAmountToCent(amount):
    """
    Convert the amount to cents.

    :param amount: The amount in dollars (e.g., 140.00)
    :return: The amount in cents (e.g., 14000)
    """
    if type(amount) == float:
        return int(amount * 100)
    if type(amount) == str:
        if '.' in amount:
            dollars, cents = amount.split('.')
            cents = (cents + '00')[:2]  # ensure 2 digits
            return int(dollars) * 100 + int(cents)
        else:
            return int(amount) * 100

with ApiClient(configuration) as api_client:

    def extractEventVariables(event):
        """Extract variables from the event."""
        user_id = event.source.user_id
        reply_token = event.reply_token
        message_text = event.message.text if hasattr(event, 'message') else None
        postback_data = event.postback.data if hasattr(event, 'postback') else None
        return user_id, reply_token, message_text, postback_data
    
    def selectDataCategoryRequest(event):
        """
        Handle the request when user wants to add new data.

        Prompt category menu to let user to pick select data category.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, _ = extractEventVariables(event)

        selectDataCategory(event)
        changeUserStatus(user_id, "addDataCategory")

    def addDataCategoryRequest(event):
        """
        Handle the request when user selected category.

        Prompt for user to input the subject of data they want to add.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, postback_data = extractEventVariables(event)

        tempData = {
            "category": postback_data
        }

        updateTempData(user_id, tempData)
        reply_message = "請輸入欲新增的項目"
        if postback_data == "food":
            reply_message = "請輸入欲新增的食物"
        changeUserStatus(user_id, "addDataSubject")        
        sendReplyMessage(line_bot_api, reply_token, reply_message)
        changeUserStatus(user_id, "addDataSubject")


    def addDataSubjectRequest(event):
        """
        Handle the event when a user requests to add a subject.

        Prompt for user to input the amount of money for the subject typed in previous subject.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, message_text, _ = extractEventVariables(event)

        tempData = getTempData(user_id)

        tempData["subject"] = message_text
        updateTempData(user_id, tempData)        
        replyMessage = "請輸入" + message_text + "的金額"
        sendReplyMessage(line_bot_api, reply_token, replyMessage)
        changeUserStatus(user_id, "addDataMoney")


    def addDataMoneyRequest(event):
        """
        Handle the event when a user requests to add the amount of money for a subject typed in previous subject.

        Prompt confirm menu to let user confirm the data they typed in. 
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, message_text, _ = extractEventVariables(event)

        tempData = getTempData(user_id)

        # Save user-typed amount to tempData
        tempData["money"] = message_text

        # Get data from tempData
        category = tempData["category"]
        subject = tempData["subject"]
        amount = tempData["money"]

        # Convert amount to cents
        amountCents = convertAmountToCent(message_text)
        exchRateCents = convertAmountToCent(getExchangeRate(user_id))
        finalAmountCents = (amountCents * exchRateCents) // 100
        tempData["exchangeRate"] = str(exchRateCents)  # or keep as int

        addition = 0
        if category == "food":
            addition = convertAmountToCent(getFoodMultiple())
        additionAmount = (finalAmountCents * addition) // 100
        additionAmountResult = finalAmountCents + additionAmount

        tempData["additionAmount"] = additionAmount
        tempData["money"] = additionAmountResult
        updateTempData(user_id, tempData)

        # Covert to message
        amount = f'{finalAmountCents} + {additionAmount}'
        
        confirmAmount(category, subject, amount, exchRateCents, reply_token) 
        
    def addDataToDatabase(event):
        """
        Add data to the database based on previous user input.

        Add data to the database and send a success message to the user.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, postback_data = extractEventVariables(event)

        try:
            tempData = getTempData(user_id)

            category = tempData["category"]
            subject = tempData["subject"]
            amount = tempData["money"]
            exchangeRate = tempData["exchangeRate"]
            additionAmount = tempData["additionAmount"]

            insertData(subject, amount, additionAmount, category)
            addDataSuccess(category, subject, amount, exchangeRate, reply_token)
            deleteTempData(user_id)
            changeUserStatus(user_id, "free")
        except Exception as e:
            sendReplyMessage(line_bot_api, reply_token, f"新增失敗: 請再試一次\n{e}")


