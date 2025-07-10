import os
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    FlexMessage,
    FlexBubble,
    TextMessage
)

from linebot.v3.messaging.models import (
    FlexBox,
    FlexText,
    FlexButton,
    PostbackAction,
    URIAction
)

# Import amount and foodmeow version
from .config import getFoodmeowVersion, getCategory

# Load dotenv
from dotenv import load_dotenv
load_dotenv()

foodmeow_version = "foodmeow v" + getFoodmeowVersion()
configuration = Configuration(access_token=os.getenv('CHANNEL_TOKEN'))

# TODO: Remove configuration from every function parameters
with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)

    def confirmTemplate(reply_token, headerTitle, bodyItems, footerItems, text=None):
        """Create a confirmation message template."""

        headerContents = [
            FlexText(
                text=headerTitle,
                weight='bold',
                size='xl',
                align='center'
            )
        ]

        bodyContents = []
        if text:
            bodyContents.append(
                FlexBox(
                    layout='baseline',
                    spacing='sm',
                    height='30px',
                    contents=[
                        FlexText(text=text, align='center')
                    ]
                )
            )

        # Use extend() to add all items from the generator
        bodyContents.extend(
            FlexBox(
                layout='baseline',
                spacing='sm',
                contents=[
                    FlexText(text=key, color='#aaaaaa',
                             size='md', flex=1, align='start'),
                    FlexText(text=str(value), wrap=True,
                             color='#666666', size='md', flex=5)
                ]
            )
            for key, value in bodyItems.items() if value is not None
        )

        footerContents = [
            FlexButton(
                style='primary',
                height='sm',
                action=PostbackAction(label=key, data=value)
            ) for key, value in footerItems.items()
        ]
        footerContents.append(
            FlexButton(
                style='link',
                height='sm',
                action=PostbackAction(label="取消", data="forceQuit")
            )
        )

        bubble = FlexBubble(
            header=FlexBox(
                layout="vertical",
                background_color='#ffeb3b',
                padding_top='xl',
                padding_bottom='xl',
                contents=headerContents
            ),
            body=FlexBox(
                layout="vertical",
                padding_top='2px',
                contents=[
                    FlexBox(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=bodyContents
                    ),
                ],
            ),
            footer=FlexBox(
                layout="vertical",
                spacing='sm',
                contents=footerContents
            ),
        )

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[
                    FlexMessage(
                        altText="資料內容確認",
                        contents=bubble
                    )
                ]
            )
        )

    def welcomeMenu(event, configuration):
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(
                        alt_text="menu",
                        contents=FlexBubble(
                            header=FlexBox(
                                layout="vertical",
                                contents=[
                                    FlexText(
                                        text="請選擇操作",
                                        align="center"
                                    ),
                                ]
                            ),
                            body=FlexBox(
                                layout="vertical",
                                contents=[
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
                                contents=[
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

    def amountMenu(event):
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
                                            data="addData food"
                                        ),
                                        style="primary",
                                    ),
                                    FlexButton(
                                        action=PostbackAction(
                                            label="其他記帳",
                                            data="addData"
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
                                            data="currencyMenu"
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

    def selectDataCategory(event):

        # Get category list
        category_list = getCategory()
        selectCategoryContent = []
        for category in category_list:
            selectCategoryContent.append(
                FlexButton(
                    action=PostbackAction(
                        label=category_list[category],
                        data=category
                    ),
                    style="primary"
                )
            )

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(
                        altText="選擇記錄類別",
                        contents=FlexBubble(
                            header=FlexBox(
                                layout="vertical",
                                contents=[
                                    FlexText(
                                        text="請選擇記帳類別",
                                        align="center"
                                    ),
                                ]
                            ),
                            body=FlexBox(
                                layout="vertical",
                                contents=selectCategoryContent
                            ),
                            footer=FlexBox(
                                layout="vertical",
                                contents=[
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

    # TODO: Let alttext show the detail of the data going to be added
    def confirmAmount(reply_token, category, subject, message):
        """Create a confirmation message before adding data."""
        categoryMap = getCategory()
        categoryLabel = categoryMap[category]

        bodyItems = {
            "類別": categoryLabel,
            "名稱": subject,
        }

        if "dataCurrency" in message:
            bodyItems["貨幣"] = f'{message["dataCurrency"]} / {message["userCurrency"]}'
            bodyItems["匯率"] = f'{message["exchangeRate"]}'
            bodyItems[message["dataCurrency"]] = message["amountMsg"]
            bodyItems[message["userCurrency"]] = message["userCurrencyMsg"]
        else:
            bodyItems["貨幣"] = message["userCurrency"]
            bodyItems["金額"] = message["amountMsg"]

        confirmTemplate(
            reply_token,
            headerTitle="新增資料確認",
            bodyItems=bodyItems,
            footerItems={
                "新增": "Yes",
            }
        )

        # line_bot_api.reply_message_with_http_info(
        #     ReplyMessageRequest(
        #         reply_token=reply_token,
        #         messages=[
        #             FlexMessage(
        #                 altText="資料資料內容確認",
        #                 contents=FlexBubble(
        #                     header=FlexBox(
        #                         layout="vertical",
        #                         background_color='#ffeb3b',
        #                         padding_top='xl',
        #                         padding_bottom='xl',
        #                         contents=[
        #                             FlexText(
        #                                 text='新增資料確認',
        #                                 weight='bold',
        #                                 size='xl',
        #                                 align='center'
        #                             ),
        #                         ]
        #                     ),
        #                     body=FlexBox(
        #                         layout="vertical",
        #                         padding_top='2px',
        #                         contents=[
        #                             FlexBox(
        #                                 layout='vertical',
        #                                 margin='lg',
        #                                 spacing='sm',
        #                                 contents=bodyContents
        #                             ),
        #                         ],
        #                     ),
        #                     footer=FlexBox(
        #                         layout="vertical",
        #                         spacing='sm',
        #                         contents=[
        #                             FlexButton(
        #                                 style='primary',
        #                                 height='sm',
        #                                 action=PostbackAction(label='新增', data='Yes')
        #                             ),
        #                             FlexButton(
        #                                 style='link',
        #                                 height='sm',
        #                                 action=PostbackAction(label='取消', data='forceQuit')
        #                             ),
        #                         ],
        #                     ),
        #                 )
        #             )
        #         ]
        #     )
        # )

    # TODO: Let alttext show the detail of the data going to be added
    def addDataSuccess(reply_token, category, subject, currency, currencyRate, money, exgCurrency=None, exgCurrencyAmount=None):
        """Send a confirmation message after adding data."""
        categoryMap = getCategory()
        categoryLabel = categoryMap[category]
        #  = {
        #     "類別": categoryLabel,
        #     "名稱": subject,
        #     "貨幣": currency,
        #     "匯率": currencyRate if currencyRate != 1.0 else None,
        #     "金額": money,
        # }

        infoItems = {
            "類別": categoryLabel,
            "名稱": subject,
        }

        if exgCurrency:
            infoItems["貨幣"] = f'{currency} / {exgCurrency}'
            infoItems["匯率"] = f'{currencyRate}'
            infoItems[currency] = money
            infoItems[exgCurrency] = exgCurrencyAmount
        else:
            infoItems["貨幣"] = currency
            infoItems["金額"] = money

        bodyContents = [
            FlexBox(
                layout='baseline',
                spacing='sm',
                contents=[
                    FlexText(text=key, color='#aaaaaa',
                             size='md', flex=1, align='start'),
                    FlexText(text=str(value), wrap=True,
                             color='#666666', size='md', flex=5)
                ]
            )
            for key, value in infoItems.items() if value is not None
        ]

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[
                    FlexMessage(
                        altText="已新增資料",
                        contents=FlexBubble(
                            body=FlexBox(
                                layout="vertical",
                                contents=[
                                    FlexText(
                                        text='已成功新增資料',
                                        weight='bold',
                                        size='xl',
                                        align='center'
                                    ),
                                    FlexBox(
                                        layout='vertical',
                                        margin='lg',
                                        spacing='sm',
                                        contents=bodyContents
                                    ),
                                ],
                            ),
                            footer=FlexBox(
                                layout="vertical",
                                spacing='sm',
                                contents=[
                                    FlexButton(
                                        style='primary',
                                        height='sm',
                                        action=PostbackAction(
                                            label='新增資料', data='addData')
                                    ),
                                    FlexButton(
                                        style='primary',
                                        height='sm',
                                        action=PostbackAction(
                                            label='新增同類型資料', data=f'addData {category}')
                                    ),
                                    FlexButton(
                                        style="link",
                                        size="sm",
                                        action=PostbackAction(
                                            label="退出、故障修復", data="forceQuit"),
                                    ),
                                ],
                            ),
                        )
                    )
                ]
            )
        )

    def giveAmountConfirm(reply_token, currency, amount):
        confirmTemplate(
            reply_token,
            headerTitle="結帳確認",
            bodyItems={
                "貨幣": currency,
                "金額": amount,
            },
            footerItems={
                "確定結帳": "Yes",
            }
        )

        # total = amount.getTotalAmount()
        # continue_data = str(total)
        # prompt_message = '目前累積總額為 ' + str(total) + " ，確認結帳？（若有小數會自動退位）"
        # line_bot_api.reply_message_with_http_info(
        #     ReplyMessageRequest(
        #         reply_token=event.reply_token,
        #         messages=[
        #             TemplateMessage(
        #                 altText='動作確認',
        #                 template=ConfirmTemplate(
        #                     title='這是ConfirmTemplate',
        #                     text=prompt_message,
        #                     actions=[
        #                         PostbackAction(
        #                             label='是',
        #                             data=continue_data
        #                         ),
        #                         PostbackAction(
        #                             label='否',
        #                             data="forceQuit"
        #                         )
        #                     ]
        #                 )
        #             )
        #         ]
        #     )
        # )

  # TODO: Let alttext show the detail of the data going to be added
    def checkoutSuccess(reply_token, currency, amount):
        """Send a confirmation message after adding data."""

        infoItems = {
            "貨幣": currency,
            "金額": amount,
        }

        bodyContents = [
            FlexBox(
                layout='baseline',
                spacing='sm',
                contents=[
                    FlexText(text=key, color='#aaaaaa',
                             size='md', flex=1, align='start'),
                    FlexText(text=str(value), wrap=True,
                             color='#666666', size='md', flex=5)
                ]
            )
            for key, value in infoItems.items() if value is not None
        ]

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[
                    FlexMessage(
                        altText="已成功結帳",
                        contents=FlexBubble(
                            body=FlexBox(
                                layout="vertical",
                                contents=[
                                    FlexText(
                                        text='已完成結帳',
                                        weight='bold',
                                        size='xl',
                                        align='center'
                                    ),
                                    FlexBox(
                                        layout='vertical',
                                        margin='lg',
                                        spacing='sm',
                                        contents=bodyContents
                                    ),
                                ],
                            ),
                            footer=FlexBox(
                                layout="vertical",
                                spacing='sm',
                                contents=[
                                    FlexButton(
                                        style='primary',
                                        height='sm',
                                        action=PostbackAction(
                                            label='新增資料', data='addData')
                                    ),
                                    FlexButton(
                                        style="link",
                                        size="sm",
                                        action=PostbackAction(
                                            label="退出、故障修復", data="forceQuit"),
                                    ),
                                ],
                            ),
                        )
                    )
                ]
            )
        )

    def getHistoryData(reply_token, bodyInfo, uncountCurrency):
        """Send a message with the history data."""

        headerContents = [
            FlexText(
                text="歷史資料",
                weight='bold',
                size='xl',
                align='center'
            )
        ]

        bodyContents = []

        # Add warning for uncounted currencies (only if not empty)
        if uncountCurrency:
            uncountCurrencyText = '有未結匯的貨幣：'
            currency_list = [f"{currency}: {count}" for currency, count in uncountCurrency.items()]
            uncountCurrencyText += ", ".join(currency_list)


            bodyContents.append(  # Use append instead of extend
                FlexBox(
                    layout='horizontal',
                    background_color='#FFCDD2',
                    contents=[
                        FlexText(text=uncountCurrencyText,
                                align='center')
                    ]
                )
            )

        # Add header row
        bodyContents.append(
            FlexBox(
                layout='horizontal',
                background_color='#F5F5F5',
                contents=[
                    FlexText(text="標題", color='#aaaaaa',
                            flex=1, align='start'),
                    FlexText(text="金額 / 加總金額", color='#aaaaaa',
                            flex=1, align='end'),
                ],
            )
        )

        # Add each data row
        for data in bodyInfo:
            bodyContents.append(  # Use append instead of extend
                FlexBox(
                    layout='horizontal',
                    contents=[
                        FlexText(text=data['subject'], wrap=True,
                                flex=1, align='start'),
                        FlexText(text=f"{data['baseAmount']} / {data['total']}",
                                size='sm', flex=2, align='end'),
                    ],
                )
            )

        bubble = FlexBubble(
            header=FlexBox(
                layout="vertical",
                background_color='#ffeb3b',
                padding_top='xl',
                padding_bottom='xl',
                contents=headerContents
            ),
            body=FlexBox(
                layout="vertical",
                padding_top='2px',
                contents=[
                    FlexBox(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=bodyContents
                    ),
                ],
            ),
        )

        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[
                    FlexMessage(
                        altText="資料內容確認",
                        contents=bubble
                    )
                ]
            )
        )

    def currencyMenu(event):
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
                                        text="匯率功能選單",
                                        align="center"
                                    ),
                                ],
                            ),
                            body=FlexBox(
                                layout="vertical",
                                contents=[
                                    FlexButton(
                                        action=PostbackAction(
                                            label="變更匯率",
                                            data="updateExchangeRate"
                                        ),
                                        style="primary",
                                    ),
                                    FlexButton(
                                        action=PostbackAction(
                                            label="變更預設貨幣",
                                            data="updateUserCurrency"
                                        ),
                                        style="primary"
                                    ),
                                    FlexButton(
                                        action=PostbackAction(
                                            label="變更新資料貨幣",
                                            data="updateNewDataCurrency"
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

    def confirmChangeCurrency(reply_token, currency):

        confirmTemplate(
            reply_token,
            headerTitle="變更貨幣確認",
            bodyItems={
                "貨幣": currency,
            },
            footerItems={
                "變更": "Yes",
            }
        )
        # """Create a confirmation message before changing currency."""

        # headerTitle = "變更貨幣確認"

        # headerContents = [
        #     FlexText(
        #         text= headerTitle,
        #         weight='bold',
        #         size='xl',
        #         align='center'
        #     ),
        # ]

        # bodyItems = {
        #     "貨幣": currency,
        # }

        # bodyContents = [
        #     FlexBox(
        #         layout='baseline',
        #         spacing='sm',
        #         contents=[
        #             FlexText(text=key, color='#aaaaaa', size='md', flex=1, align='start'),
        #             FlexText(text=str(value), wrap=True, color='#666666', size='md', flex=5)
        #         ]
        #     )
        #     for key, value in bodyItems.items() if value is not None
        # ]

        # footerItems = {
        #     "變更": "Yes",
        #     "取消": "forceQuit"
        # }

        # footerContents = [
        #     FlexButton(
        #         style='primary',
        #         height='sm',
        #         action=PostbackAction(label=key, data=value)
        #     )
        #     for key, value in footerItems.items()
        # ]

        # line_bot_api.reply_message_with_http_info(
        #     ReplyMessageRequest(
        #         reply_token=reply_token,
        #         messages=[
        #             FlexMessage(
        #                 altText="資料內容確認",
        #                 contents=FlexBubble(
        #                     header=FlexBox(
        #                         layout="vertical",
        #                         background_color='#ffeb3b',
        #                         padding_top='xl',
        #                         padding_bottom='xl',
        #                         contents=headerContents
        #                     ),
        #                     body=FlexBox(
        #                         layout="vertical",
        #                         padding_top='2px',
        #                         contents=[
        #                             FlexBox(
        #                                 layout='vertical',
        #                                 margin='lg',
        #                                 spacing='sm',
        #                                 contents=bodyContents
        #                             ),
        #                         ],
        #                     ),
        #                     footer=FlexBox(
        #                         layout="vertical",
        #                         spacing='sm',
        #                         contents=footerContents
        #                     ),
        #                 )
        #             )
        #         ]
        #     )
        # )

    def confirmChangeExchangeRate(exchangeRate, prompt_message, reply_token):
        confirmTemplate(
            reply_token,
            headerTitle="變更匯率確認",
            bodyItems={
                "匯率": exchangeRate,
            },
            footerItems={
                "變更": exchangeRate,
            }
        )

        # continue_data = exchangeRate
        # line_bot_api.reply_message_with_http_info(
        #     ReplyMessageRequest(
        #         reply_token=reply_token,
        #         messages=[
        #             TemplateMessage(
        #                 altText='動作確認',
        #                 template=ConfirmTemplate(
        #                     title='加入資料庫確認',
        #                     text=prompt_message,
        #                     actions=[
        #                         PostbackAction(
        #                             label='是',
        #                             data=continue_data
        #                         ),
        #                         PostbackAction(
        #                             label='否',
        #                             data="forceQuit"
        #                         )
        #                     ]
        #                 )
        #             )
        #         ]
        #     )
        # )

    def confirmExchangeWhileCheckout(reply_token, currency, amount, exchangeRate):
        confirmTemplate(
            reply_token,
            headerTitle="貨幣轉換確認",
            bodyItems={
                "貨幣": currency,
                "金額": amount,
                "匯率": exchangeRate
            },
            footerItems={
                "進行轉換": "confirmExchange",
                # "自訂匯率": "customExchangeRate",
            },
            text="您有資料尚未結匯"
        )
