import sys
sys.path.append('.')
from config import getFoodMultiple

import os
from dotenv import load_dotenv
#from linebot import models
load_dotenv()

from pymongo import MongoClient
#from bson.objectid import ObjectId

from datetime import datetime

load_dotenv()

conn = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = conn.foodmeow
data = db.data

def insertFoodData(subject, money: float):
    addition = money * getFoodMultiple()
    total = money + addition
    data.insert_one(
        {
            "time": datetime.now(),
            "subject": subject,
            "money": money,
            "addition": addition,
            "total": total,
        }
    )
    return "新增" + " " + str(total) + " 元 " + subject + " 成功"

def insertData(subject, money: float):
    data.insert_one(
        {
            "time": datetime.now(),
            "subject": subject,
            "money": money,
            "addition": 0,
            "total": money,
        }
    )
    return "新增" + subject + "成功"


def getTotalAmount():
    totalAmount = 0.0
    foods = data.find()
    for amount in foods:
        money = amount['total']
        totalAmount += float(money)
    return totalAmount

def giveAmount(money):
    data.insert_one({
        "time": datetime.now(),
        "subject": datetime.now().strftime("%Y/%m/%d"),
        "money": -money,
        "addition": 0,
        "total": -money,
    })
    return True

def getHistory():
    foods = data.find().sort("time", -1).limit(100)
    message = ""
    count = 0
    for food in foods:
        count += 1
        reply = ""
        reply = str(count) + ". " + str(food['subject']) + " " + str(food['money']) + "/" + str(food['total']) + '\n'
        message += reply
    return message