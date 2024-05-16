import os
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.append('.')
from config import getFoodMultiple

from pymongo import MongoClient
from bson.objectid import ObjectId

from datetime import datetime

import user

load_dotenv()

conn = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = conn.foodmeow
users = db.users
data = db.data


def checkUserExist(userid):
    user = users.find_one({
        "userId": userid
    })
    if(user == None):
        users.insert_one({
            "userId": userid,
            "status": "free",
        })
        return "NewUser"
    return "OldUser"


def checkUserStatus(userId):
    user = users.find_one({
        "userId": userId,
    })
    return user['status']


def changeUserStatus(userId, status):
    users.update_one({
        "userId": userId,
    },
        {
        '$set': {
            "status": status,
        }
    })


def insertFoodData(object, money):
    addition = money * getFoodMultiple()
    print(addition)
    data.insert_one(
        {
            "time": datetime.now(),
            "object": object,
            "money": money,
            "addition": addition,
            "total": money + addition,
        }
    )
    print(addition)
    return "新增" + "成功"

def insertdata(subject, money):
    data.insert_one(
        {
            "time": datetime.now(),
            "subject": object,
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
        "subject": datetime.now().strftime("%m/%d"),
        "money": 0,
        "addition": 0,
        "total": -money,
    })
    return "success"

def getHistory():
    foods = data.find().sort("time", -1)
    message = ""
    for food in foods:
        reply = ""
        reply = str(food['subject']) + " " + str(food['money']) + "/" + str(food['total']) + '\n'
        message += reply
    return message

def getTempData(userId):
    user = users.find_one({
        "userId": userId,
    })
    return user['tempData']

def updateTempData(userId, data):
    user = users.find_one({
        "userId": userId,
    })
    if data == "":
        print("empty")
    elif user['tempData'] != "":
        data = user['tempData'] + " " + data
    users.update_one({
        "userId": userId,
    },
    {
        '$set': {
            "tempData": data,
        }
    })

def deleteTempData(userId):
    users.find_one_and_update({
        "userId": userId,
    },
    {
        '$set': {
            "tempData": "",
        }
    })

def getCurrencyExchangeRate(userId):
    user = users.find_one({
        "userId": userId,
    })
    return user['currencyExchangeRate']

money = 100.0
print(getCurrencyExchangeRate("Ua7ae783c1c186dd1ac7e355157038344"))


#print(user.getTempData("Ua7ae783c1c186dd1ac7e355157038344"))
#print(checkUserStatus('12345'))
#print(changeUserStatus("Ua7ae783c1c186dd1ac7e355157038344", "free"))
#print(deleteTempData("Ua7ae783c1c186dd1ac7e355157038344"))

#for i in range(0,2):
#    for j in range(0,2):
#print(insertFoodData("麥噹", 100))
#    for j in range(0,1):
#print(giveAmount(1245.5))
#print(getTotalAmount())
#print(getHistory())

