import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
#from bson.objectid import ObjectId
load_dotenv()

'''
Connect to MongoDB.
'''

conn = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = conn.foodmeow
users = db.users

'''
Check user exist in database.
'''
def checkUserExist(profile):
    userId = profile.user_id
    displayName = profile.display_name
    user = users.find_one({
        "userId": userId
    })
    if(user is None):
        users.insert_one({
            "userId": userId,
            "displayName": displayName,
            "status": "free",
            "tempData": "",
            "currencyExchangeRate": 1,
        })
        return "NewUser"

'''
Check user exist in status
'''
def checkUserStatus(userId):
    user = users.find_one({
        "userId": userId,
    })
    return user['status']

'''
Change status when user is running some function.
'''
def changeUserStatus(userId, status):
    users.update_one({
        "userId": userId,
    },
    {
        '$set': {
            "status": status,
        }
    })

'''
Temp data for user who is operate some function.
'''

def updateTempData(userId, data):
    user = users.find_one({
        "userId": userId,
    })
    if user['tempData'] != "":
        data = user['tempData'] + " " + data
    users.update_one({
        "userId": userId,
    },
    {
        '$set': {
            "tempData": data,
        }
    })

def getTempData(userId):
    user = users.find_one({
        "userId": userId,
    })
    return user['tempData']    

def deleteTempData(userId):
    users.find_one_and_update({
        "userId": userId,
    },
    {
        '$set': {
            "tempData": "",
        }
    })

'''
Currency exchange rate
'''

def getCurrencyExchangeRate(userId):
    user = users.find_one({
        "userId": userId,
    })
    return user['currencyExchangeRate']


def updateCurrencyExchangeRate(userId, currencyExchangeRate: float):
    users.update_one({
        "userId": userId,
    },
    {
        '$set': {
            "currencyExchangeRate": currencyExchangeRate,
        }
    })

'''
Clear all data to default if there is anything error.
'''
def clearDataToDefault(userId):
    deleteTempData(userId)
    changeUserStatus(userId, "free")
