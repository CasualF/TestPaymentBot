from aiogram import Bot, Dispatcher, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold

import sys
import logging
import asyncio
import utils
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
                         reply_markup=utils.create_order_markup)


@dp.callback_query(lambda query: query.data == 'my:checkout')
async def create_order_handler(query: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.paying)
    curr_state = await state.get_state()
    await bot.send_message(text=curr_state, chat_id=query.from_user.id)


@dp.message()
async def answer(message: types.Message):
    await message.reply('Такой команды нет, введи существующую!')


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
