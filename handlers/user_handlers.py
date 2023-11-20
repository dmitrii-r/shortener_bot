from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router: Router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message) -> None:
    """
    Обработчик запуска бота.
    Выводит приветственное сообщение.
    """
    user_name = message.from_user.first_name
    start_text = (
        f"Привет, {user_name}! Это бот для создания событий и получения "
        f"коротких ссылок на них."
    )
    await message.answer(text=start_text)


@router.message(Command(commands="help"))
async def process_help_command(message: Message):
    message_text = (
        "Для создания нового события выберите в меню или введите команду "
        "/add_event\n"
        "Для просмотра имеющихся событий выберите в меню или введите команду "
        "/get_events\n"
        "Для просмотра всех событий со статистикой их использования выберите "
        "в меню или введите команду /get_usages_count"
    )
    await message.answer(message_text)
