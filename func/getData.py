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
   getUserCurrency
)
from .menu import getHistoryData
from . import amount
from .amount import getLatestData
from .config import getFoodMultiple
from .utils import convertAmountToCent, convertCentToDecimalString

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

def getOneData(_id):
    return amount.getOneData(_id)

with ApiClient(configuration) as api_client:

    def extractEventVariables(event):
        """Extract variables from the event."""
        user_id = event.source.user_id
        reply_token = event.reply_token
        message_text = event.message.text if hasattr(event, 'message') else None
        postback_data = event.postback.data if hasattr(event, 'postback') else None
        return user_id, reply_token, message_text, postback_data
    
    def getHistoryDataRequest(event):
        user_id, reply_token, _, _ = extractEventVariables(event)
        bodyInfo = []

        def appendRecord(data):
            """
            Append a record to body.
            """
            bodyInfo.append({
                "subject": data['subject'],
                "baseAmount": convertCentToDecimalString(data['baseAmount']),
                "total": convertCentToDecimalString(data['total']),
                "currency": displayCurrency
            })
        
        latestData = getLatestData(20)
        checkoutCurrency = getUserCurrency(user_id)
        uncountCurrency = {}
        message = ""
        count = 0

        for data in latestData:
            count += 1
            displayCurrency = checkoutCurrency

            # Compatible with old data added < v1.2.1
            # `money` field changed name to `total` field in v1.2.2 
            if 'baseAmount' not in data and 'money' in data:
                data['baseAmount'] = data['money']
            # Data before 1.3.0 or 2025/4/30 does not have currency field
            if 'currency' not in data:
                continue
            # Check currency or exgCurrency have checkoutCurrency
            if data['currency'] == checkoutCurrency:
                appendRecord(data)
                continue
            elif 'exgCurrency' in data and data['exgCurrency'] == checkoutCurrency:
                appendRecord(data)
                continue
            else:
                if data['currency'] not in uncountCurrency:
                    uncountCurrency[data['currency']] = 0
                uncountCurrency[data['currency']] += 1

        print(uncountCurrency)

        getHistoryData(reply_token, bodyInfo, uncountCurrency)
             




    #         if type(fetchedData['baseAmount']) == int:
    #             fetchedData['baseAmount'] = convertCentToDecimalString(fetchedData['baseAmount'])
    #             fetchedData['total'] = convertCentToDecimalString(fetchedData['total'])
            
    #         reply = f"{count}. {fetchedData['subject']} {fetchedData['baseAmount']}/{fetchedData['total']}\n"
    #         message += reply
    # return message
    

    