from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

conn = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = conn.foodmeow
currency_data = db.currency

def currentTime():
    return datetime.now(timezone.utc) + timedelta(hours=8)

def insertCurrencyData(baseCurrency, currencyExchangeRate):
    try:
        result = currency_data.insert_one(
            {
                "time": currentTime(),
                "baseCurrency": baseCurrency,
                "currencyExchangeRate": currencyExchangeRate,
            }
        )
        return result
    except Exception as e:
        return e
    
def getCurrencyData(currency):
  try:
    result = currency_data.find_one(
        {
            "baseCurrency": currency,
            "time": {"$gte": currentTime() - timedelta(hours=8)}
        },
        sort=[("time", -1)]
    )
    return result
  except Exception as e:
    return e
  
  