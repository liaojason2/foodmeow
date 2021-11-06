from linebot.models import (
    Template, TextMessage, TextSendMessage,
    TemplateSendMessage, ButtonsTemplate, MessageTemplateAction, PostbackAction, FlexSendMessage, messages,
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot import (
    LineBotApi, WebhookHandler
)
import os
from dotenv import load_dotenv
from linebot.models.actions import PostbackAction
from linebot.models.flex_message import BubbleContainer, BoxComponent, TextComponent, ButtonComponent
load_dotenv()

line_bot_api = LineBotApi(os.environ.get("CHANNEL_TOKEN"))

def welcomeMenu(event):
    flex_message = FlexSendMessage(
        alt_text="menu",
        contents=BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text="請選擇操作", align="center"),
                ],
            ),
            footer=BoxComponent(
                layout="vertical",
                contents=[
                    ButtonComponent(
                        action=PostbackAction(label="記帳", data="add"),
                    ),
                ],
            ),
        ),
    ),
    line_bot_api.reply_message(event.reply_token, flex_message)
