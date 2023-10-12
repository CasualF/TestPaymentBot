from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

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


# @dp.message(F.filter('web_app_data'))
# async def create_order_handler(message: Message, state: FSMContext):
#     await state.set_state(UserState.paying)
#     data = json.loads(message.web_app_data.data)
#     await message.answer(data, reply_markup=utils.create_order_markup)


async def check_data_handler(request: Request):
    bot: Bot = request.app["bot"]

    data = await request.post()
    try:
        data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return json_response({"ok": False, "err": "Unauthorized"}, status=401)
    return json_response({"ok": True, "data": data.user.dict()})


@dp.message()
async def answer(message: types.Message):
    await message.reply('Такой команды нет, введи существующую!')


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
