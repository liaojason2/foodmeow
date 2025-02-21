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

# DEPRECATED: insertFoodData Merge with insertData in 1.2.0

# def insertFoodData(userId, subject: str, money: float):
#     addition = money * getFoodMultiple()
#     total = money + addition
#     data.insert_one(
#         {
#             "time": currentTime,
#             "subject": subject,
#             "category": "food",
#             "money": money,
#             "addition": addition,
#             "total": total,
#         }
#     )
#     return "新增" + " " + str(total) + " 元 " + subject + " 成功"


def insertData(subject: str, money: float, addition: float, category: str):
    try:
        data.insert_one(
            {
                "time": currentTime,
                "subject": subject,
                "category": category,  # todo function
                "money": money,
                "addition": addition,
                "total": money,
            }
        )
        return True
    except Exception as e:
        return e


def getTotalAmount():
    totalAmount = 0.0
    foods = data.find()
    for amount in foods:
        money = amount['total']
        totalAmount += float(money)
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
