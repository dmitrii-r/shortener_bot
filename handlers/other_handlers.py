from aiogram import Router
from aiogram.types import Message

router: Router = Router()


@router.message()
async def send_echo(message: Message):
    message_text = (
        "Некорректный ввод. Если нужна помощь выбери в меню "
        "или введи команду /help."
    )
    await message.answer(message_text)
