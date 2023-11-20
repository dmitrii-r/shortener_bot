from aiogram import Bot
from aiogram.types import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

commands = {
    "/add_event": "Добавить новое событие.",
    "/get_events": "Просмотреть текущие события.",
    "/get_usages_count": "Показать статистику использования событий.",
    "/help": "Справка по работе бота.",
}


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command=command, description=description)
        for command, description in commands.items()
    ]
    await bot.set_my_commands(main_menu_commands)


def confirm_keyboard() -> InlineKeyboardMarkup:
    confirm_button = InlineKeyboardButton(
        text="Подтвердить.", callback_data="confirm"
    )
    cancel_button = InlineKeyboardButton(
        text="Отменить", callback_data="cancel"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[confirm_button], [cancel_button]]
    )

    return keyboard


def cancel_keyboard() -> InlineKeyboardMarkup:
    cancel_button = InlineKeyboardButton(
        text="Отменить", callback_data="cancel"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[cancel_button]],
    )

    return keyboard


def create_events_keyboard(
    width: int, events: list[dict]
) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    for event in events:
        button_text = f"Событие: {event['summary']}"
        buttons.append(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"used_url={event['id']}",
            )
        )

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()
