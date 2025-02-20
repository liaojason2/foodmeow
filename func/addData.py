import os
from dotenv import load_dotenv
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
    
)
from linebot.v3 import WebhookHandler
from .user import (
    changeUserStatus, updateTempData, getTempData, getExchangeRate, deleteTempData
)
from .menu import confirmAmount, selectDataCategory
from .amount import insertData

load_dotenv()

configuration = Configuration(access_token=os.getenv('CHANNEL_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

def passUserTypedAmountToConfirmMenu(userId, event, tempData):
    """Pass user-typed amount to confirm menu."""
    replyToken = event.reply_token

    category = tempData["category"]
    subject = tempData["subject"]
    amount = tempData["money"]

    exchangeRate = getExchangeRate(userId)
    amount = str(int(float(amount) * float(exchangeRate)))
    prompt_message = f'請確認是否要將 {amount} 的 {subject} 加入資料庫中'
    if exchangeRate != 1.0:
        prompt_message += f'（匯率 {exchangeRate}）。'
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
    
    def selectDataCategoryRequest(event):
        """
        Handle the request to open a menu to select a data category for data.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, _ = extractEventVariables(event)

        selectDataCategory(event, configuration)
        changeUserStatus(user_id, "addDataCategory")

    def addDataCategoryRequest(event):
        """Handle the request to add category for data."""
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, postback_data = extractEventVariables(event)

        tempData = {"category": postback_data}
        updateTempData(user_id, tempData)        
        sendReplyMessage(line_bot_api, reply_token, "請輸入欲新增的項目")
        changeUserStatus(user_id, "addDataSubject")

    def addDataSubjectRequest(event):
        """Handle the request to add subject for data."""
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, message_text, _ = extractEventVariables(event)

        tempData = getTempData(user_id)
        tempData["subject"] = message_text
        updateTempData(user_id, tempData)        
        sendReplyMessage(line_bot_api, reply_token, f"請輸入{message_text}的金額")
        changeUserStatus(user_id, "addDataMoney")

    def addDataMoneyRequest(event):
        """Handle the request to add the amount of money for data."""
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, message_text, _ = extractEventVariables(event)

        tempData = getTempData(user_id)
        tempData["money"] = message_text
        updateTempData(user_id, tempData)
        passUserTypedAmountToConfirmMenu(user_id, event, tempData)  
        
    def addDataToDatabase(event):
        """Add data to the database based on previous user input."""
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, _ = extractEventVariables(event)

        try:
            tempData = getTempData(user_id)
            insertData(tempData["subject"], tempData["money"], tempData["category"])
            deleteTempData(user_id)
            changeUserStatus(user_id, "free")
            sendReplyMessage(line_bot_api, reply_token, "新增成功")
        except:
            sendReplyMessage(line_bot_api, reply_token, "新增失敗，請重新輸入")


