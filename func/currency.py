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
from .menu import confirmChangeExchangeRate
from .user import updateExchangeRate
from .config import getFoodMultiple
from .utils import convertAmountToCent, convertCentToDecimalString

load_dotenv()

configuration = Configuration(access_token=os.getenv('CHANNEL_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

with ApiClient(configuration) as api_client:

    def extractEventVariables(event):
        """Extract variables from the event."""
        user_id = event.source.user_id
        reply_token = event.reply_token
        message_text = event.message.text if hasattr(event, 'message') else None
        postback_data = event.postback.data if hasattr(event, 'postback') else None
        return user_id, reply_token, message_text, postback_data
    
    def changeCurrencyRateRequest(event):
        """
        Handle the request when user wants to change currency rate.
        """
        user_id, reply_token, _, _ = extractEventVariables(event)
        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="請輸入匯價")]
            )
        )

        changeUserStatus(user_id, "updateExchangeRate")

    def changeCurrencyRateAmountRequest(event):

        user_id, reply_token, message, postback_data = extractEventVariables(event)
        line_bot_api = MessagingApi(api_client)

        exchangeRate = str(message)
        prompt_message = '請確認匯價為 ' + str(message)
        confirmChangeExchangeRate(
            exchangeRate, prompt_message, reply_token)
        
        changeUserStatus(user_id, "updateExchangeRateConfirm")

    def changeCurrencyRateAmount(event):
        user_id, reply_token, _, postback_data = extractEventVariables(event)
        line_bot_api = MessagingApi(api_client)
        
        exchangeRate = convertAmountToCent(postback_data)
        updateExchangeRate(user_id, exchangeRate)
        changeUserStatus(user_id, "free")
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="變更成功")]
            )
        )



  
