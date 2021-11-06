import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
load_dotenv()

conn = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = conn.foodmeow
users = db.users

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

print(checkUserExist("12345"))