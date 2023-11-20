import os

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from utils.db_utils import (
    get_all_urls,
    get_hash_value,
    insert_url,
    update_usage_count,
)

load_dotenv()

short_domain = os.getenv("SHORT_DOMAIN")

router: Router = Router()


@router.message(F.text.startswith("http"))
async def shorten_url(message: Message):
    """
    Обработчик сообщений, сокращающий длинные URL.
    Срабатывает, если сообщение начинается с http.
    Отправляет сообщение с коротким URL в чат.
    Сохраняет, длинный URL и его хэш в БД.
    Обновляет количество использований ссылки.
    """
    long_url = message.text
    hash_value = await get_hash_value(long_url)

    if not hash_value:
        hash_value = await insert_url(long_url)

    short_url = f"{short_domain}{hash_value}"
    await update_usage_count(hash_value)
    await message.reply(
        f"Оригинальная ссылка: {long_url}\nСокращенная ссылка: {short_url}"
    )


@router.message(Command(commands="get_usages_count"))
async def process_get_usages_count_command(message: Message):
    """
    Обработчик команды /get_usages_count.
    Отправляет в чат список всех имеющихся в БД коротких ссылок со статистикой
    их использования.
    """
    urls = await get_all_urls()

    if urls:
        message_text = (
            "Список коротких ссылок со статистикой их использования:\n"
        )
        for url in urls:
            hash_value = url["hash_value"]
            short_url = f"{short_domain}{hash_value}"
            message_text += (
                f"{short_url} - Использована {url['usage_count']} раз(а)\n"
            )
    else:
        message_text = "В базе данных нет коротких ссылок."

    await message.reply(message_text)


@router.message()
async def send_echo(message: Message):
    message_text = "Некорректный ввод. Просто отправь длинную ссылку."
    await message.answer(message_text)
