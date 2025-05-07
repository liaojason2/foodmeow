from datetime import datetime, timedelta
from pymongo import MongoClient
from .config import getFoodMultiple
import os
from dotenv import load_dotenv
load_dotenv()


currentTime = datetime.now() + timedelta(hours=8)

load_dotenv()

conn = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = conn.foodmeow
data = db.data

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
        
def convertCentToDecimalString(amount):
    """
    Convert the amount in cents to a decimal string.

    :param amount: The amount in cents (e.g., 14000)
    :return: The amount in dollars as a string (e.g., "140.00")
    """
    if type(amount) == int:
        dollars = amount // 100
        cents = amount % 100
        return f"{dollars}.{cents:02d}"
    else:
        raise ValueError("Amount must be an integer.")

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
        reply = ""
        reply = str(count) + ". " + str(food['subject']) + " " + \
            str(food['money']) + "/" + str(food['total']) + '\n'
        message += reply
    return message
