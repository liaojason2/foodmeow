import sys
sys.path.append('.')
from config import getFoodMultiple

import os
from dotenv import load_dotenv
from linebot import models
load_dotenv()



from pymongo import MongoClient
from bson.objectid import ObjectId

from datetime import datetime

load_dotenv()

conn = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = conn.foodmeow
data = db.data

def insertFoodData(object, money):
    addition = money * getFoodMultiple()
    data.insert_one(
        {
            "time": datetime.now(),
            "object": object,
            "money": money,
            "addition": addition,
            "total": money + addition,
        }
    )
    return "新增" + " " + str(money+addition) + " 元 " + object + " 成功"

def insertData(object, money):
    data.insert_one(
        {
            "time": datetime.now(),
            "object": object,
            "money": money,
            "addition": 0,
            "total": money,
        }
    )
    return "新增" + object + "成功"


def getTotalAmount():
    totalAmount = 0
    count = 0
    foods = data.find().sort("time", -1).limit(100)
    for amount in foods:
        total = amount['total']
        print(total, end=" ")
        if(total <= 0):
            count += 1
        if(count == 3):
            break
        totalAmount += total
        print(totalAmount)
    return "總額" + str(totalAmount)

def giveAmount(money):
    data.insert_one({
        "time": datetime.now(),
        "object": datetime.now().strftime("%Y/%m/%d"),
        "money": 0,
        "addition": 0,
        "total": -money,
    })
    return "success"

def getHistory():
    foods = data.find().sort("time", -1).limit(100)
    message = ""
    for food in foods: 
        reply = ""
        reply = str(food['object']) + " " + str(food['money']) + "/" + str(food['total']) + '\n'
        message += reply
    return message