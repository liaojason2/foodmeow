from datetime import datetime, timedelta
from pymongo import MongoClient
from .config import getFoodMultiple
import os
from dotenv import load_dotenv
load_dotenv()

from .utils import convertAmountToCent, convertCentToDecimalString

currentTime = datetime.now() + timedelta(hours=8)

load_dotenv()

conn = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = conn.foodmeow
data = db.data

def insertData(subject: str, baseAmount: int, addition: int, total: int, category: str):
    try:
        data.insert_one(
            {
                "time": currentTime,
                "subject": subject,
                "category": category,
                "baseAmount": baseAmount,
                "addition": addition,
                "total": total,
            }
        )
        return True
    except Exception as e:
        return e

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


def giveAmount(money):
    data.insert_one({
        "time": currentTime,
        "subject": currentTime.strftime("%Y/%m/%d"),
        "money": -money,
        "addition": 0,
        "total": -money,
    })
    return True


def getHistory():
    foods = data.find().sort("time", -1).limit(20)
    message = ""
    count = 0
    for food in foods:
        count += 1

        # Compatible with old data added < v1.2.1
        # `money` field changed name to `total` field in v1.2.2 
        if 'baseAmount' not in food and 'money' in food:
            food['baseAmount'] = food['money']

        # Compatible with bug when refactor in 1.2.0 > 1.2.1
        # https://github.com/liaojason2/foodmeow/blob/248291c0b9ab5fc9e195eb2fbd95cb10a4b339ec/func/amount.py
        if food['baseAmount'] == food['total']: 
            food['baseAmount'] /= 1.5 
            food['baseAmount'] = round(food['baseAmount'], 2)

        if type(food['baseAmount']) == int:
            food['baseAmount'] = convertCentToDecimalString(food['baseAmount'])
            food['total'] = convertCentToDecimalString(food['total'])
        
        reply = f"{count}. {food['subject']} {food['baseAmount']}/{food['total']}\n"
        message += reply
    return message
