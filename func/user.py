import os
#from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
#from bson.objectid import ObjectId
load_dotenv()

conn = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = conn.foodmeow
users = db.users

def checkUserExist(profile):
    userId = profile.user_id
    user = users.find_one({
        "userId": userId
    })
    if(user == None):
        users.insert_one({
            "userId": userId,
            "status": "free",
        })
        return "NewUser"