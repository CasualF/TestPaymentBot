from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold
from aiohttp import ClientSession

import sys
import logging
import asyncio
import utils
import json
from config import settings

storage = MemoryStorage()
bot = Bot(settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=storage)


class MyCallback(CallbackData, prefix='my'):
    type: str


class UserState(StatesGroup):
    paying = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer_sticker(utils.CAT_STICKER)
    await message.answer(f"Привет, {hbold(message.from_user.first_name)}! Нажми на меню и выбери что хочешь купить",
                         reply_markup=utils.menu_markup)


@dp.message(F.web_app_data)
async def web_app(message: Message, state: FSMContext) -> None:
    data = json.loads(message.web_app_data.data)
    response = data['data']
    if not any(i['quantity'] for i in response):
        await message.answer('Заказ пуст!')
    else:
        await state.set_state(UserState.paying)
        products = [i for i in response if i['quantity']>0]
        products = {'products': products}
        await state.update_data(products)
        response = utils.collected_items_str(response)
        await message.answer(response, reply_markup=utils.create_order_markup)


@dp.callback_query(F.data == 'submit', UserState.paying)
async def make_payment(query: CallbackData, state: FSMContext):
    async with ClientSession() as session:
        products = await state.get_data()
        products = json.dumps(products)
        headers = {
            'api-key': settings.ACCESS_TOKEN
        }
        async with session.post(url=settings.CREATE_ORDER_URL,
                                data=products,
                                headers=headers) as response:
            if response.status == 201:
                response = await response.json()
                checkout_url = response.get('checkout_url')
                markup = utils.get_checkout_web_app(checkout_url.replace('http', 'https'))
                if checkout_url is not None:
                    # await state.update_data({'uuid': response.get('uuid')})
                    await bot.send_message(chat_id=query.from_user.id,
                                           text=f'Заказ оформлен!\nОплатите кнопкой ниже 👇',
                                           reply_markup=markup)
            else:
                await bot.send_message(chat_id=query.from_user.id,
                                       text='Не получилось оформить заказ :(\n Попробуйте оформить заново',
                                       reply_markup=utils.menu_markup)


@dp.message(F.web_app_data.data.get('uuid'))
async def checkout_pay(message: Message, state: FSMContext):
    async with ClientSession() as session:
        data = json.loads(message.web_app_data.data)
        uuid = data["uuid"]
        url = settings.ORDER_URL + uuid
        async with session.post(url=url) as response:
            response = await response.json()
            if response.get('status') == 'PAID':
                await state.clear()
                await message.answer(text='Заказ оплачен успешно!',
                                     reply_markup=utils.menu_markup)
            else:
                await message.answer(text='Заказ не был оплачен.',
                                     reply_markup=utils.menu_markup)


@dp.message(F.text == '❌ Выход')
async def exit_bot(message: types.Message):
    await message.reply('Пока! \nЧтобы запустить заново -> /start', reply_markup=types.ReplyKeyboardRemove())


@dp.callback_query(F.data == 'exit')
async def exit_bot_inline(query: CallbackData):
    await bot.send_message(chat_id=query.from_user.id,
                           text='Пока! \nЧтобы запустить заново -> /start',
                           reply_markup=types.ReplyKeyboardRemove())


@dp.message()
async def echo(message: types.Message):
    await message.reply('Такой команды нет, введите существующую!')


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
