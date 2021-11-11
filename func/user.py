import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
#from bson.objectid import ObjectId
load_dotenv()

conn = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = conn.foodmeow
users = db.users

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
        })
        return "NewUser"
        
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
