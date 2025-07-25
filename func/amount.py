from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from .utils import convertAmountToCent, convertCentToDecimalString

load_dotenv()

conn = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = conn.foodmeow
data = db.data

def currentTime():
    return datetime.now(timezone.utc) + timedelta(hours=8)

def insertData(
        subject: str, baseAmount: int, addition: int, total: int, category: str, currency: str, 
        exgCurrency: dict):
    try:
        result = data.insert_one(
            {
                "time": currentTime(),
                "subject": subject,
                "category": category,
                "currency": currency,
                "baseAmount": baseAmount,
                "addition": addition,
                "total": total,
                "currencyExchange": exgCurrency,
            }
        )
        return result
    except Exception as e:
        return e

def updateCurrencyExchangeData(id, currency, exchangeResult):
    result = data.update_one(
        filter={'_id': id},
        update={
            "$set": {
                f"currencyExchange.{currency}": exchangeResult
            }
        }
    )
    return result

def getTotalAmount():
    totalAmount = 0
    foods = data.find()
    for amount in foods:
        money = amount['total']
        # Compatible with old data added < v1.2.1
        if isinstance(money, float) == True:
            totalAmount += int(money*100)
        # Version 1.2.2 and later use int to store cent  
        else:
            totalAmount += money
    totalAmount = convertCentToDecimalString(totalAmount)
    return totalAmount


def checkout(amount: int, currency: str):
    data.insert_one({
        "time": currentTime(),
        "subject": currentTime().strftime("%Y/%m/%d"),
        "currency": currency,
        "category": 'checkout',
        "baseAmount": -amount,
        "addition": 0,
        "total": -amount,
    })
    return True

def getOneData(_id):
    return data.find_one({'_id': _id})

def getLatestData(limit):
    record = data.find().sort("time", -1).limit(limit)
    return record

# def getHistory():
#     fetchedDatas = data.find().sort("time", -1).limit(20)
#     message = ""
#     count = 0
#     for fetchedData in fetchedDatas:
#         count += 1

#         # Compatible with old data added < v1.2.1
#         # `money` field changed name to `total` field in v1.2.2 
#         if 'baseAmount' not in fetchedData and 'money' in fetchedData:
#             fetchedData['baseAmount'] = fetchedData['money']

#         # DEPRECATED: Manually fix thr wrong data in 1.2.3
#         # # Compatible with bug when refactor in 1.2.0 > 1.2.1
#         # # https://github.com/liaojason2/foodmeow/blob/248291c0b9ab5fc9e195eb2fbd95cb10a4b339ec/func/amount.py
#         # if food['baseAmount'] == food['total']:
#         #     # Check attr exist
#         #     if hasattr('food', 'category')
#         #     food['baseAmount'] /= 1.5 
#         #     food['baseAmount'] = round(food['baseAmount'], 2)

#         if type(fetchedData['baseAmount']) == int:
#             fetchedData['baseAmount'] = convertCentToDecimalString(fetchedData['baseAmount'])
#             fetchedData['total'] = convertCentToDecimalString(fetchedData['total'])
        
#         reply = f"{count}. {fetchedData['subject']} {fetchedData['baseAmount']}/{fetchedData['total']}\n"
#         message += reply
#     return message
