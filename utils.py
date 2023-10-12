import requests
from config import settings
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup


CAT_STICKER = 'CAACAgUAAxkBAAMTZODxSVrx-Au63rwBN1KalR7coR0AAuIFAAKncZlWsMfRBFaNBHQwBA'

menu_button = KeyboardButton(text='🍽️ Меню', web_app=WebAppInfo(url=settings.MENU_URL))
exit_button = KeyboardButton(text='❌ Выход')

menu_markup = ReplyKeyboardMarkup(keyboard=[[
    menu_button, exit_button
]], resize_keyboard=True)


exit_button_inline = InlineKeyboardButton(text='❌ Выход', callback_data='exit')
submit_button = InlineKeyboardButton(text='✅ Подтвердить заказ', callback_data='submit')

create_order_markup = InlineKeyboardMarkup(inline_keyboard=[[
    submit_button, exit_button_inline
]], resize_keyboard=True)


def get_checkout_web_app(url):
    markup = ReplyKeyboardMarkup(keyboard=[[
        KeyboardButton(text='Оплатить', web_app=WebAppInfo(url=url)),
        exit_button
    ]], resize_keyboard=True)
    return markup


def collected_items_str(data: list[{}]):
    result = f'Вы заказали:\n'
    total = 0
    for i in data:
        if i['quantity'] > 0:
            total += i['price'] * i['quantity']
            result += f'{i["name"]} - {i["price"] * i["quantity"]} - кол-во {i["quantity"]}\n'
    return result + f'\nВ общем: {total} тенге'
