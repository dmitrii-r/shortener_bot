from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from keyboards.keyboards import create_events_keyboard
from utils.db_utils import (
    get_all_events,
    get_usages_count,
    update_usage_count_by_id,
)

router: Router = Router()


@router.message(Command(commands="get_events"))
async def process_get_events_command(message: Message):
    """
    Получение списка коротких ссылок на события.
    """
    events = await get_all_events()

    if events:
        keyboard = create_events_keyboard(1, events)

        await message.answer(
            "Выберите событие на которое нужна ссылка:", reply_markup=keyboard
        )
    else:
        await message.answer("Список событий пуст.")


@router.message(Command(commands="get_usages_count"))
async def process_get_events_command(message: Message):
    """
    Получение списка событий со статистикой их использования.
    """
    events = await get_usages_count()

    if events:
        message_text = "Список событий со статистикой их использования:\n"
        for event in events:
            summary = event["summary"]
            usage_count = event["usage_count"]
            message_text += (
                f"Ссылка на событие {summary} - "
                f"Использована {usage_count} раз(а)\n"
            )
    else:
        message_text = "В базе данных нет событий."

    await message.answer(message_text)


@router.callback_query(F.data.startswith("used_url"))
async def process_update_usages_counter(callback: CallbackQuery):
    event_id = int(callback.data.split("=")[1])
    upd_event = await update_usage_count_by_id(event_id)
    upd_summary = upd_event["summary"]
    upd_url = upd_event["long_url"]

    await callback.message.answer(
        f"Ссылка на событие [{upd_summary}]({upd_url})",
        parse_mode="MarkdownV2",
    )
    await callback.answer()
