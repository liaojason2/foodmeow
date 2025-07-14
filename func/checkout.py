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
    changeUserStatus, updateTempData, getTempData, getExchangeRate, deleteTempData, getDataCurrency, getUserCurrency
)
from .menu import giveAmountConfirm, confirmExchangeWhileCheckout, checkoutSuccess
from .amount import checkout, getLatestData
from .config import getFoodMultiple, getCategory
from .utils import convertAmountToCent, convertCentToDecimalString
from .currency import getCurrencyRate, updateExchangeCurrencyToDatabase
from .user import changeUserStatus

load_dotenv()

configuration = Configuration(access_token=os.getenv('CHANNEL_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

def sendReplyMessage(
    line_bot_api: MessagingApi,
    reply_token: str,
    message_text: str
) -> None:
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

    def requestCheckout(event):
        """
        Handle the request when user wants to checkout.
        """
        user_id, reply_token, _, _ = extractEventVariables(event)

        record = getLatestData(200)

        checkoutCurrency = getUserCurrency(user_id)
        total = {checkoutCurrency: 0}

        for data in record:
            # Data before 1.3.0 or 2025/4/30 does not have currency field
            if 'currency' not in data:
                continue
            if data['category'] == 'checkout':
                break
            # Check currency or exgCurrency have checkoutCurrency
            if data['currency'] == checkoutCurrency:
                total[checkoutCurrency] += data['total']
                continue
            elif 'currencyExchange' in data and checkoutCurrency in data['currencyExchange']:
                total[checkoutCurrency] += data['currencyExchange'][checkoutCurrency]['total']
            # The data does not have checkoutCurrency
            else:
                newCurrency = data['currency']
                if newCurrency not in total:
                    total[newCurrency] = {'amount': 0, 'data': []}
                total[newCurrency]['amount'] += data['total']
                total[newCurrency]['data'].append(data)  # Append the entire MongoDB object

        # check there is other currency, if there is pass to `updateExchangeCurrencyToDatabase`
        if len(total) > 1 or checkoutCurrency not in total:
            for currency, item in total.items():
                if currency != checkoutCurrency:
                    exchangeRate = round(getCurrencyRate(currency, checkoutCurrency), 4)
                    currencyMsg = f"{currency} / {checkoutCurrency}"
                    amount = convertCentToDecimalString(item['amount'])

                    tempData = {
                        'currency': checkoutCurrency,
                        'exchangeRate': exchangeRate,
                        'data': item['data']
                    }

                    updateTempData(user_id, tempData)
                    confirmExchangeWhileCheckout(reply_token, currencyMsg, amount, exchangeRate)
                    changeUserStatus(user_id, "updateCurrencyWhileCheckout")
        else:
            amount = convertCentToDecimalString(total[checkoutCurrency])
            giveAmountConfirm(reply_token, checkoutCurrency, amount)
            tempData = {'currency': checkoutCurrency, 'amount': amount}
            updateTempData(user_id, tempData)
            changeUserStatus(user_id, "checkoutConfirm")

    def updateExchangeCurrency(event):

        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, _ = extractEventVariables(event)
        tempData = getTempData(user_id)
        categoryList = getCategory()

        if not tempData:
            print("No temp data found")
            return 0

        exchangeRate = tempData['exchangeRate']
        data = tempData['data']

        for item in data:

            id = item['_id']
            baseAmount = item['baseAmount']
            category = item['category']
            
            # DEPRECATED: Refactor to category list in 1.3.2
            #addition = convertAmountToCent(getFoodMultiple()) if category == "food" else 0
            addition = convertAmountToCent(categoryList[category]['addition'])
            if addition is None:
                addition = 0
            
            updateExchangeCurrencyToDatabase(event, [item], addition, exchangeRate)

            # exchangeRateCents = convertAmountToCent(exchangeRate, 4)

            # userCurrencyBaseAmount = int((baseAmount * 100 * exchangeRateCents) // 1000000)
            # userCurrencyAdditionAmount = (userCurrencyBaseAmount * addition) // 100
            # userCurrencyTotal = userCurrencyBaseAmount + userCurrencyAdditionAmount

            # # Execute bulk update
            # updateCurrencyExchangeData(
            #     id, currency, exchangeRate, userCurrencyBaseAmount, userCurrencyAdditionAmount, userCurrencyTotal
            # )

        # TODO: Show the convert amount and some more detail data 
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="已完成轉換，請重新進行結帳")]
            )
        )
        deleteTempData(user_id)

    def requestCheckoutComplete(event) -> None:
        """
        Handle the request when user confirms the checkout.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, _ = extractEventVariables(event)

        tempData = getTempData(user_id)
        amount = tempData['amount']
        currency = tempData['currency']

        amount = convertAmountToCent(amount)

        checkout(amount, currency)
        
        checkoutSuccess(reply_token, currency, tempData['amount'])

        deleteTempData(user_id)
        changeUserStatus(user_id, "free")
