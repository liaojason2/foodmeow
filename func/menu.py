from linebot import LineBotApi
from linebot.models import TemplateSendMessage, FlexSendMessage, PostbackTemplateAction
from linebot.models.template import ConfirmTemplate
from linebot.models.actions import PostbackAction
from linebot.models.flex_message import BubbleContainer, BoxComponent, TextComponent, ButtonComponent

import sys
sys.path.append('./func')
import user

import os
from dotenv import load_dotenv
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
                            data="payAmount"
                        ),
                        style="primary"
                    ),
                    ButtonComponent(
                        action=PostbackAction(
                            label="歷史",
                            data="historyAmount"
                        ),
                        style="primary"
                    ),
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
        )
    ),
    line_bot_api.reply_message(event.reply_token, flex_message)


def confirm(event):
    foodObject = user.getTempData(event.source.user_id)
    continue_data = foodObject + " " + event.message.text
    prompt_message = '請確認是否要將 ' + event.message.text + " 的 " + foodObject + "加入資料庫中"
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
                    data="forcequit"
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)
