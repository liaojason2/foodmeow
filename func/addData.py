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
    changeUserStatus, updateTempData, getTempData, getExchangeRate, deleteTempData, getDataCurrency, getUserCurrency
)
from .menu import selectDataCategory, confirmAmount, addDataSuccess
from . import amount
from .amount import insertData
from .config import getFoodMultiple, getCategory
from .utils import convertAmountToCent, convertCentToDecimalString
from .currency import getCurrencyRate, multiCurrencyConversion

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

        categoryList = getCategory()

        tempData = getTempData(user_id)

        # Save user-typed amount to tempData
        tempData["amount"] = message_text
        tempData["baseAmount"] = convertAmountToCent(message_text)

        # Get data from previous entries
        category = tempData["category"]
        subject = tempData["subject"]
        amountCents = convertAmountToCent(tempData["amount"])

        ## If the data currency is different is with user currency,
        ## count the exchange rate and convert the amount to user currency
        # if isExchange:
        #     try:
        #         exchangeRateVal = getCurrencyRate(dataCurrency, userCurrency)
        #         exchangeRateCents = convertAmountToCent(exchangeRateVal, 4)
        #         userCurrencyAmount = int((amountCents * 100 * exchangeRateCents) // 1000000)
        #         tempData["userCurrencyBaseAmount"] = userCurrencyAmount
        #         exchangeRate = f"{exchangeRateVal:.4f}"  # Format to 4 decimal places
        #         tempData["exchangeRate"] = exchangeRate
        #     except Exception as e:
        #         sendReplyMessage(line_bot_api, reply_token, f"取得匯率失敗: {e}")
        
        # Addition for specific categories

        # DEPRECATED: Refactor to category list in 1.3.2
        # addition = convertAmountToCent(getFoodMultiple()) if category == "food" else 0
        
        addition = convertAmountToCent(categoryList[category]['addition'])
        if addition is None:
            addition = 0

        additionAmount = (amountCents * addition) // 100
        totalAmount = amountCents + additionAmount


        tempData["additionAmount"] = additionAmount
        tempData["amount"] = totalAmount

        # Currency Exchange
        ## Get user based currency and data currency
        userCurrency = getUserCurrency(user_id)
        dataCurrency = getDataCurrency(user_id)

        tempData["userCurrency"] = userCurrency
        tempData["dataCurrency"] = dataCurrency


        ## Define some variables
        isExchange = userCurrency != dataCurrency
        exchangeRate = 1
        userCurrencyBaseAmount = None
        userCurrencyAdditionAmount = None

        ## Count for currency difference (include addition)
        if isExchange:
            exchangeRateVal = getCurrencyRate(dataCurrency, userCurrency)

            exchangeResult = multiCurrencyConversion(
                amountCents, addition, dataCurrency, userCurrency, exchangeRateVal
            )

            exchangeResult = exchangeResult[userCurrency]

            userCurrencyBaseAmount = exchangeResult['baseAmount']
            userCurrencyAdditionAmount = exchangeResult['addition']
            exchangeRate = exchangeResult['exchangeRate']

            tempData["exchangeRate"] = exchangeRate
            tempData["userCurrencyBaseAmount"] = userCurrencyBaseAmount
            tempData["userCurrencyAdditionAmount"] = userCurrencyAdditionAmount
            tempData["userCurrencyTotal"] = exchangeResult['total']

        # Store data to tempData
        updateTempData(user_id, tempData)

        #Prompt confirm message
        def formatAmount(cents):
            return f"{cents // 100}.{cents % 100:02d}"

        amountMsg = f"{formatAmount(amountCents)} + {formatAmount(additionAmount)}"
        userCurrencyMsg = None
        if isExchange:
            userCurrencyMsg = f"{formatAmount(userCurrencyBaseAmount)} + {formatAmount(userCurrencyAdditionAmount)}"

        if isExchange:
            msg = {
            'userCurrency': userCurrency,
            'dataCurrency': dataCurrency,
            "amountMsg": amountMsg,
            "userCurrencyMsg": userCurrencyMsg,
            "exchangeRate": exchangeRate
            }
        else:
            msg = {
            'userCurrency': userCurrency,
            "amountMsg": amountMsg,
            }

        confirmAmount(reply_token, category, subject, msg)
        
    def addDataToDatabase(event):
        """
        Add data to the database based on previous user input.

        Add data to the database and send a success message to the user.
        """
        line_bot_api = MessagingApi(api_client)
        user_id, reply_token, _, postback_data = extractEventVariables(event)

        try:
            tempData = getTempData(user_id)

            # Define Variables
            currencyExchange = {}
            exgCurrency = None
            exgCurrencyAmount = 0
            userCurrency = tempData["userCurrency"]
            exchangeRate = tempData['exchangeRate'] if 'exchangeRate' in tempData else 1

            # Define inserted data
            category = tempData["category"]
            subject = tempData["subject"]
            baseAmount = tempData["baseAmount"]
            amount = tempData["amount"]
            additionAmount = tempData["additionAmount"]
            currency = tempData["dataCurrency"]
            if "exchangeRate" in tempData:
                currencyExchange = {
                    userCurrency: {
                        'exchangeRate': tempData['exchangeRate'],
                        'baseAmount': tempData["userCurrencyBaseAmount"],
                        'addition': tempData["userCurrencyAdditionAmount"],
                        'total': tempData["userCurrencyTotal"]
                    }
                }
            insertData(subject, baseAmount, additionAmount, amount, category, currency, currencyExchange)
            
            # Prompt success message
            amount = convertCentToDecimalString(amount)
            if currencyExchange:
                exgCurrency = userCurrency
                exgCurrencyAmount = convertCentToDecimalString(currencyExchange[userCurrency]['total'])
            addDataSuccess(reply_token, category, subject, currency, exchangeRate, amount, exgCurrency, exgCurrencyAmount)
            
            # Clean up
            deleteTempData(user_id)
            changeUserStatus(user_id, "free")
        except Exception as e:
            sendReplyMessage(line_bot_api, reply_token, f"新增失敗: 請再試一次\n{e}")


