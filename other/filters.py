from typing import Any
from aiogram.filters import BaseFilter
from aiogram import types, Bot

from config import CHANNEL_ID
from database.db import DataBase


class ChatJoinFilter(BaseFilter):

    async def __call__(self, message: types.Message, bot: Bot) -> Any:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID,
                                                user_id=message.from_user.id)

        if chat_member.status in ["member", "creator", "administrator"]:
            return True

        return False


class RegisteredFilter(BaseFilter):

    async def __call__(self, callback: types.CallbackQuery) -> Any:
        return not await DataBase.get_user(callback.from_user.id) is None
