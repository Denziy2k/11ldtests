import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, WebAppInfo)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
CHANNEL = "@cachedmemory"
CHANNEL_URL = "https://t.me/cachedmemory"
AUTHOR_URL = "https://t.me/denziy2k"

WELCOME = (
    "<b>Слово в слово</b> 📝\n\n"
    "Тренажёр словарных слов по русскому языку для 11ЛД: "
    "запоминай слово, собирай его из букв и проверяй, как пишешь на самом деле. "
    "Есть 4 уровня сложности, озвучка и словарь с ударениями.\n\n"
    "Чтобы пользоваться ботом, нужно подписаться на канал "
    f"{CHANNEL}."
)
OK_TEXT = "Всё готово, ты подписан ✅\nЖми кнопку и тренируйся!"
NO_TEXT = "Подписка не найдена. Подпишись на канал и нажми «Я подписался» ещё раз."

log = logging.getLogger("bot")
dp = Dispatcher()


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(CHANNEL, user_id)
        return m.status in ("member", "administrator", "creator")
    except Exception as e:
        log.warning("Не удалось проверить подписку (бот должен быть админом канала): %s", e)
        return False


def kb_subscribe() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться на канал", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check")],
        [InlineKeyboardButton(text="👤 Автор", url=AUTHOR_URL)],
    ])


def kb_open() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть тест", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="👤 Автор", url=AUTHOR_URL)],
    ])


@dp.message(CommandStart())
async def start(msg: Message, bot: Bot):
    if await is_subscribed(bot, msg.from_user.id):
        await msg.answer(WELCOME + "\n\n" + OK_TEXT, reply_markup=kb_open())
    else:
        await msg.answer(WELCOME, reply_markup=kb_subscribe())


@dp.callback_query(F.data == "check")
async def check(cb: CallbackQuery, bot: Bot):
    if await is_subscribed(bot, cb.from_user.id):
        await cb.message.answer(OK_TEXT, reply_markup=kb_open())
        await cb.answer()
    else:
        await cb.answer(NO_TEXT, show_alert=True)


async def main():
    logging.basicConfig(level=logging.INFO)
    if not TOKEN or not WEBAPP_URL:
        raise SystemExit("Задай переменные окружения BOT_TOKEN и WEBAPP_URL")
    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
