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
from linebot.models.actions import *
from linebot.models.flex_message import *
load_dotenv()


line_bot_api = LineBotApi(os.getenv("CHANNEL_TOKEN"))


def meow(event):
    try:
        message = TemplateSendMessage(
            alt_text="Device Not Support",
            template=ButtonsTemplate(
                thumbnail_image_url=None,
                title="開始使用本系統",
                text="請選擇您要使用的動作",
                actions=[
                    PostbackAction(
                        label="新增款項",
                        text="@NewAmount"
                    ),
                    MessageTemplateAction(
                        label="結帳 (UI 系統開發中)",
                        text="結帳"
                    ),
                    MessageTemplateAction(
                        label="刪除款項 (UI 系統開發中)",
                        text="@DeleteAmount"
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="Error"))


def richmenutest(event):
    flex_message = FlexSendMessage(
        alt_text="menu",
        contents=BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text="請選擇操作"),
                ],
            ),
            footer=BoxComponent(
                layout="vertical",
                contents=[
                    ButtonComponent(
                        action=PostbackAction(label="記帳", data="hello"),
                    ),
                ],
            ),
        ),
    ),
    line_bot_api.reply_message(event.reply_token, flex_message)
