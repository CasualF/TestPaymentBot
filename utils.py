import requests
from config import settings
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from main import MyCallback

CAT_STICKER = 'CAACAgUAAxkBAAMTZODxSVrx-Au63rwBN1KalR7coR0AAuIFAAKncZlWsMfRBFaNBHQwBA'


create_order_markup = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Перейти к оплате 💰')]
])


async def create_order(products):
    access_token = settings.ACCESS_TOKEN
    create_order_url = settings.CREATE_ORDER_URL
    products = [{
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
        } for product in products]
    payload = {'products': products,
               "description": "Оплата с телеграмм"}
    result = requests.post(url=create_order_url,
                           data=payload,
                           headers={'Authorization': 'Bearer ' + access_token})
    result = result.json()
    checkout_url = result.get('checkout_url')
    return checkout_url
