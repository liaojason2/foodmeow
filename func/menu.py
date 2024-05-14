from linebot.v3.messaging import (
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    FlexMessage,
    FlexBubble,
    TemplateMessage,
    ConfirmTemplate
    
)

from linebot.v3.messaging.models import (
    FlexBox,
    FlexText,
    FlexButton,
    PostbackAction,
    URIAction
)

# Import amount and foodmeow version
from . import amount
from .config import getFoodmeowVersion

# Load dotenv
from dotenv import load_dotenv
load_dotenv()


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

def amountMenu(event, configuration):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(
                        altText="menu",
                        contents=FlexBubble(
                            header=FlexBox(
                                layout="vertical",
                                contents=[
                                    FlexText(
                                        text="記帳功能選項",
                                        align="center"
                                    ),
                                ],
                            ),
                            body=FlexBox(
                                layout="vertical",
                                contents=[
                                    FlexButton(
                                        action=PostbackAction(
                                            label="食物記帳",
                                            data="addFoodAmount"
                                        ),
                                        style="primary",
                                    ),
                                    FlexButton(
                                        action=PostbackAction(
                                            label="其他記帳",
                                            data="addAmount"
                                        ),
                                        style="primary"
                                    ),
                                    FlexButton(
                                        action=PostbackAction(
                                            label="總額",
                                            data="totalAmount"
                                        ),
                                        style="primary"
                                    ),
                                    FlexButton(
                                        action=PostbackAction(
                                            label="結帳",
                                            data="giveAmount"
                                        ),
                                        style="primary"
                                    ),
                                    FlexButton(
                                        action=PostbackAction(
                                            label="歷史",
                                            data="getHistoryAmount"
                                        ),
                                        style="primary"
                                    ),
                                    FlexButton(
                                        action=PostbackAction(
                                            label="變更匯率",
                                            data="updateExchangeRate"
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
                                ],
                            ),
                            footer=FlexBox(
                                layout="vertical",
                                contents=[
                                    FlexText(
                                        text=foodmeow_version,
                                        align="center"
                                    ),
                                ],
                            ),
                        )
                    )     
                ]
            )
        )

def confirmAmount(subject, amount, prompt_message, reply_token, configuration):
    continue_data = subject + " " + amount
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[
                    TemplateMessage(
                        altText='動作確認',
                        template=ConfirmTemplate(
                            title='加入資料庫確認',
                            text=prompt_message,
                            actions=[
                                PostbackAction(
                                    label='是',
                                    data=continue_data
                                ),
                                PostbackAction(
                                    label='否',
                                    data="forceQuit"
                                )
                            ]
                        )
                    )
                ]
            )
        )

def giveAmountConfirm(event, configuration):
    total = amount.getTotalAmount()
    continue_data = str(total)
    prompt_message = '目前累積總額為 ' + str(total) + " ，確認結帳？（若有小數會自動退位）"
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TemplateMessage(
                        altText='動作確認',
                        template=ConfirmTemplate(
                            title='這是ConfirmTemplate',
                            text=prompt_message,
                            actions=[
                                PostbackAction(
                                    label='是',
                                    data=continue_data
                                ),
                                PostbackAction(
                                    label='否',
                                    data="forceQuit"
                                )
                            ]
                        )
                    )
                ]
            )
        )

def confirmChangeExchangeRate(exchangeRate, prompt_message, reply_token, configuration):
    continue_data = exchangeRate
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=[
                TemplateMessage(
                    altText='動作確認',
                    template=ConfirmTemplate(
                        title='加入資料庫確認',
                        text=prompt_message,
                        actions=[
                            PostbackAction(
                                label='是',
                                data=continue_data
                            ),
                            PostbackAction(
                                label='否',
                                data="forceQuit"
                            )
                        ]
                    )
                )
            ]
        )
    )
