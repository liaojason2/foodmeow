from bson.objectid import ObjectId  # 這東西再透過ObjectID去尋找的時候會用到
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot import (
    LineBotApi, WebhookHandler
)
from pymongo import MongoClient
import os

from flask import Flask, request, abort
from dotenv import load_dotenv
import reply

load_dotenv()


# connection
conn = MongoClient(os.getenv("MONGODB_CONNECTION"))
db = conn.foodmeow
fooddata = db.fooddata


app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("CHANNEL_TOKEN"))
handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if(event.message.text == "開啟選單"):
        reply.richmenutest(event)

    data = {}
    data['item'] = "apple"
    data['price'] = 20
    fooddata.insert_one(data)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()
