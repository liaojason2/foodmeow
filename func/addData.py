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

# DEPRECATED: addFoodAmount Merge with addData in 1.2.0

# def passUserTypedAmountToConfirmMenu(userId, event, tempData):
#     """Pass user-typed amount to confirm menu."""
#     replyToken = event.reply_token
#     user_id = event.source.user_id

#     category = tempData["category"]
#     subject = tempData["subject"]
#     amount = tempData["money"]

#     # Get exchange rate
#     exchangeRate = getExchangeRate(userId)
#     # Count exchange rate and convert to integer
#     amount = float(amount) * float(exchangeRate)
#     tempData["exchangeRate"] = exchangeRate
#     updateTempData(user_id, tempData)
    
#     # Add food multiple
#     addition = 0.0
#     if category == "food":
#         addition = getFoodMultiple()

#     additionAmount = amount * addition
#     additionResult = amount + additionAmount

#     amount = additionResult
#     tempData = getTempData(user_id)
#     tempData["money"] = amount
#     updateTempData(user_id, tempData)

#     # Covert to message
#     amount = f'{amount} (+{additionAmount})'
    
#     confirmAmount(category, subject, amount, exchangeRate, replyToken)

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
    
    def selectDataCategoryRequest(event):
        """
        Handle the request when user wants to add new data.

        Prompt for user to input the subject of they want to add.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, _ = extractEventVariables(event)

        selectDataCategory(event)
        changeUserStatus(user_id, "addDataCategory")

    def addDataCategoryRequest(event):
        """

        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, postback_data = extractEventVariables(event)

        tempData = {
            "category": postback_data
        }

        updateTempData(user_id, tempData)        
        sendReplyMessage(line_bot_api, reply_token, "請輸入欲新增的項目")
        changeUserStatus(user_id, "addDataSubject")


    def addDataSubjectRequest(event):
        """
        Handle the request when user wants to add new data.

        Prompt for user to input the subject of they want to add.
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

        Prompt for user to input the subject of they want to add.
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

        # Count exchange rate
        exchangeRate = getExchangeRate(user_id)
        amount = float(amount) * float(exchangeRate)
        tempData["exchangeRate"] = exchangeRate # Add exchange rate to tempData
        
        # Add specify category multiple condition
        addition = 0.0
        if category == "food":
            addition = getFoodMultiple()

        additionAmount = amount * addition
        amount = amount + additionAmount

        tempData['additionAmount'] = additionAmount # Add addition amount to tempData
        tempData["money"] = amount # Add calculated amount to tempData
        updateTempData(user_id, tempData)

        # Covert to message
        amount = f'{amount} (+{additionAmount})'
        
        confirmAmount(category, subject, amount, exchangeRate, reply_token) 
        
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


