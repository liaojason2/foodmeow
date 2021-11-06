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

line_bot_api = LineBotApi(os.getenv("CHANNEL_TOKEN"))

def welcomeMenu(event):
    flex_message = FlexSendMessage(
        alt_text="menu",
        contents=BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text="請選擇操作", align="center"),
                ],
            ),
            body=BoxComponent(
                layout="vertical",
                contents=[
                    ButtonComponent(
                        action=PostbackAction(
                            label="記帳",
                            data="Amount"
                        ),
                        style="primary",
                        offsetBottom="5px"
                    ),   
                    ButtonComponent(
                        action=PostbackAction(
                            label="About Foodmeow",
                            data="AboutFoodmeow"
                        ),
                        style="primary"
                    )
                ],
            ),
            footer=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(
                        text="foodmeow v1.0",
                        align="center"
                    ),
                ],
            ),
        ),
    ),
    line_bot_api.reply_message(event.reply_token, flex_message)

def amountMenu(event):
    flex_message = FlexSendMessage(
        alt_text="menu",
        contents=BubbleContainer(
            header=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(text="記帳功能選項", align="center"),
                ],
            ),
            body=BoxComponent(
                layout="vertical",
                contents=[
                    ButtonComponent(
                        action=PostbackAction(
                            label="食物記帳",
                            data="Amount"
                        ),
                        style="primary",
                        offsetBottom="sm"
                    ),   
                    ButtonComponent(
                        action=PostbackAction(
                            label="其他記帳",
                            data="AboutFoodmeow"
                        ),
                        style="primary"
                    ),
                    ButtonComponent(
                        action=PostbackAction(
                            label="其他記帳",
                            data="AboutFoodmeow"
                        ),
                        style="primary"
                    ),
                    ButtonComponent(
                        action=PostbackAction(
                            label="其他記帳",
                            data="AboutFoodmeow"
                        ),
                        style="primary"
                    )
                ],
            ),
            footer=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(
                        text="foodmeow v1.0",
                        align="center"
                    ),
                ],
            ),
        ),
    ),
    line_bot_api.reply_message(event.reply_token, flex_message)
