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
import currencyapicom
from .user import (
    changeUserStatus, updateTempData, getTempData, deleteTempData
)
from .menu import confirmChangeExchangeRate, confirmChangeCurrency, confirmTemplate
from .user import updateExchangeRate, updateUserCurrency, updateNewDataCurrency, getUserCurrency
from .utils import convertAmountToCent
from .amount import updateCurrencyExchangeData
from .getData import getOneData

load_dotenv()

configuration = Configuration(access_token=os.getenv('CHANNEL_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

currency_api_client = currencyapicom.Client(os.getenv('CURRENCY_COM_API_KEY'))

def getCurrencyRate(base_currency, target_currency):

    result = currency_api_client.latest(base_currency, [target_currency])
    result = result['data'][target_currency]['value']
    return result

def multiCurrencyConversion(amount: int, addition, currency, convertCurrency, exchangeRate):

    exchangeRateCents = convertAmountToCent(exchangeRate, 4)
    userCurrencyBaseAmount = int((amount * 100 * exchangeRateCents) // 1000000)
    userCurrencyAdditionAmount = (userCurrencyBaseAmount * addition) // 100
    userCurrencyTotal = userCurrencyBaseAmount + userCurrencyAdditionAmount

    exchangeRate = f'{exchangeRate:.4f}'

    data = {
        convertCurrency:{
            "exchangeRate": exchangeRate,
            "baseAmount": userCurrencyBaseAmount,
            "addition": userCurrencyAdditionAmount,
            "total": userCurrencyTotal
        }
    }

    return data

def updateExchangeCurrencyToDatabase(event, record, addition, exchangeRate):

    user_id, reply_token, _, _ = extractEventVariables(event)

    print(record)

    for item in record:

        id = item['_id']
        data = getOneData(id)

        baseAmount = data['baseAmount']
        currency = data['currency']
        userCurrency = getUserCurrency(user_id)

        exchangeResult = multiCurrencyConversion(
            baseAmount,
            addition,
            currency,
            userCurrency,
            exchangeRate
        )

        exchangeResult = exchangeResult[userCurrency]

        updateCurrencyExchangeData(
            id, userCurrency, exchangeResult
        )

        changeUserStatus(user_id, "free")

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

    def updateUserCurrencyRequest(event):
        """
        Handle the request when user wants to change user currency.
        """
        user_id, reply_token, _, _ = extractEventVariables(event)
        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="請輸入新的預設貨幣")]
            )
        )

        changeUserStatus(user_id, "updateUserCurrency")

    def updateUserCurrencyConfirm(event):
        user_id, reply_token, message, _ = extractEventVariables(event)
        line_bot_api = MessagingApi(api_client)

        tempData = getTempData(user_id)

        newCurrency = message

        tempData = {
            "userCurrency": newCurrency
        }
        updateTempData(user_id, tempData)
            
        # Prompt user to confirm the new currency
        confirmChangeCurrency(
            reply_token, newCurrency)
        
        changeUserStatus(user_id, "updateUserCurrencyConfirm")




    def confirmUpdateUserCurrency(event):
        user_id, reply_token, _, _ß = extractEventVariables(event)
        line_bot_api = MessagingApi(api_client)

        tempData = getTempData(user_id)
        newCurrency = tempData['userCurrency']

        # Update the user currency in the database
        updateUserCurrency(user_id, newCurrency)
        deleteTempData(user_id)

        changeUserStatus(user_id, "free")
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="變更成功，新的預設貨幣為 " + newCurrency)]
            )
        )

    def updateNewDataCurrencyRequest(event):
        """
        Handle the request when user wants to change data currency.
        """
        user_id, reply_token, _, _ = extractEventVariables(event)
        line_bot_api = MessagingApi(api_client)

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="請輸入新的資料所要使用的貨幣")]
            )
        )

        changeUserStatus(user_id, "updateNewDataCurrency")

    def updateNewDataCurrencyConfirm(event):
        user_id, reply_token, message, _ = extractEventVariables(event)
        line_bot_api = MessagingApi(api_client)

        tempData = getTempData(user_id)

        newCurrency = message

        tempData = {
            "dataCurrency": newCurrency
        }
        updateTempData(user_id, tempData)
            
        # Prompt user to confirm the new currency
        confirmTemplate(
            reply_token,
            headerTitle="變更新增資料貨幣確認",
            bodyItems={
                "新貨幣": newCurrency,
            },
            footerItems={
                "新增": "Yes",
            }
        )
        
        changeUserStatus(user_id, "updateNewDataCurrencyConfirm")

    def confirmUpdateNewDataCurrency(event):
        user_id, reply_token, _, _ = extractEventVariables(event)
        line_bot_api = MessagingApi(api_client)

        tempData = getTempData(user_id)
        newCurrency = tempData['dataCurrency']

        # Update the data currency in the database
        updateNewDataCurrency(user_id, newCurrency)
        deleteTempData(user_id)

        changeUserStatus(user_id, "free")
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="變更成功，新的資料貨幣為 " + newCurrency)]
            )
        )



  
