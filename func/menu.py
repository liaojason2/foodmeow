import sys
import os
'''
from linebot import LineBotApi
from linebot.models import TemplateSendMessage, FlexSendMessage, PostbackTemplateAction
from linebot.models.template import ConfirmTemplate
from linebot.models.actions import PostbackAction
from linebot.models.flex_message import BubbleContainer, BoxComponent, TextComponent, ButtonComponent
'''
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer,
    FlexBubble,
    FlexContainer
)

from linebot.v3.messaging.models import (
    FlexBox,
    FlexText,
    FlexButton,
    TextMessage,
    PostbackAction,
    URIAction
)

from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

# Import amount and foodmeow version
from . import amount
from .config import getFoodmeowVersion

# Load dotenv
from dotenv import load_dotenv
load_dotenv()


line_bot_api = LineBotApi(os.getenv("CHANNEL_TOKEN"))
foodmeow_version = "foodmeow v" + getFoodmeowVersion()

def welcomeMenu(event, configuration):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(
                        alt_text="menu",
                        contents=FlexBubble(
                            header=FlexBox(
                                layout="vertical",
                                contents= [
                                    FlexText(
                                        text="請選擇操作",
                                        align="center"
                                    ),
                                ]                                
                            ),               
                            body=FlexBox(
                                layout="vertical",
                                contents= [
                                    FlexButton(
                                        action=PostbackAction(
                                            label="記帳",
                                            data="Amount"
                                        ),
                                        style="primary",
                                    ),
                                    FlexButton(
                                        action=URIAction(
                                            label="About Foodmeow",
                                            uri="https://www.foodmeow.com/about"
                                        ),
                                        style="primary"
                                    ),
                                    FlexButton(
                                        action=PostbackAction(
                                            label="退出、故障修復",
                                            data="forceQuit"
                                        ),
                                        style="primary"
                                    ),
                                ]
                            ),
                            footer=FlexBox(
                                layout="vertical",
                                contents= [
                                    FlexText(
                                        text=foodmeow_version,
                                        align="center"
                                    ),
                                ]
                            )
                        )
                    )
                ]
            )
        )
'''
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
                            data="addFoodAmount"
                        ),
                        style="primary",
                        offsetBottom="sm"
                    ),
                    ButtonComponent(
                        action=PostbackAction(
                            label="其他記帳",
                            data="addAmount"
                        ),
                        style="primary"
                    ),
                    ButtonComponent(
                        action=PostbackAction(
                            label="總額",
                            data="totalAmount"
                        ),
                        style="primary"
                    ),
                    ButtonComponent(
                        action=PostbackAction(
                            label="結帳",
                            data="giveAmount"
                        ),
                        style="primary"
                    ),
                    ButtonComponent(
                        action=PostbackAction(
                            label="歷史",
                            data="getHistoryAmount"
                        ),
                        style="primary"
                    ),
                    ButtonComponent(
                        action=PostbackAction(
                            label="變更匯率",
                            data="updateExchangeRate"
                        ),
                        style="primary"
                    ),
                    ButtonComponent(
                        action=PostbackAction(
                            label="退出、故障修復",
                            data="forceQuit"
                        ),
                        style="primary"
                    ),
                ],
            ),
            footer=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(
                        text = foodmeow_version,
                        align = "center"
                    ),
                ],
            ),
        )
    ),
    line_bot_api.reply_message(event.reply_token, flex_message)


def confirmAmount(subject, amount, prompt_message, reply_token):
    continue_data = subject + " " + amount
    message = TemplateSendMessage(
        alt_text='動作確認',
        template=ConfirmTemplate(
            title='加入資料庫確認',
            text=prompt_message,
            actions=[
                PostbackTemplateAction(
                    label='是',
                    data=continue_data
                ),
                PostbackTemplateAction(
                    label='否',
                    data="forceQuit"
                )
            ]
        )
    )
    line_bot_api.reply_message(reply_token, message)

def giveAmountConfirm(event):
    total = amount.getTotalAmount()
    continue_data = total
    prompt_message = '目前累積總額為 ' + str(total) + " ，確認結帳？（若有小數會自動退位）"
    message = TemplateSendMessage(
        alt_text='動作確認',
        template=ConfirmTemplate(
            title='這是ConfirmTemplate',
            text=prompt_message,
            actions=[
                PostbackTemplateAction(
                    label='是',
                    data=continue_data
                ),
                PostbackTemplateAction(
                    label='否',
                    data="forceQuit"
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)

def confirmChangeExchangeRate(exchangeRate, prompt_message, reply_token):
    continue_data = exchangeRate
    message = TemplateSendMessage(
        alt_text='動作確認',
        template=ConfirmTemplate(
            title='加入資料庫確認',
            text=prompt_message,
            actions=[
                PostbackTemplateAction(
                    label='是',
                    data=continue_data
                ),
                PostbackTemplateAction(
                    label='否',
                    data="forceQuit"
                )
            ]
        )
    )
    line_bot_api.reply_message(reply_token, message)
'''