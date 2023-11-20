from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from keyboards.keyboards import cancel_keyboard, confirm_keyboard
from utils.db_utils import save_event_to_database

router: Router = Router()

storage = MemoryStorage()


class FSMFillForm(StatesGroup):
    fill_summary = State()
    fill_long_url = State()
    fill_location = State()
    fill_description = State()
    fill_date_start = State()
    fill_date_end = State()
    confirmation = State()


@router.message(Command(commands="cancel"), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text="Вы прервали заполнение события.\n"
        "Чтобы снова перейти к заполнению выберите в меню "
        "или введите команду /add_event"
    )
    await state.clear()


@router.message(Command(commands="add_event"), StateFilter(default_state))
async def process_add_event_command(message: Message, state: FSMContext):
    await message.answer(
        text="Заполните все поля события. Если хотите прервать заполнение "
        "введите команду /cancel\n"
    )
    await message.answer(text="Пожалуйста, введите название события.")
    await state.set_state(FSMFillForm.fill_summary)


@router.message(StateFilter(FSMFillForm.fill_summary))
async def process_long_url_sent(message: Message, state: FSMContext):
    await state.update_data(summary=message.text)
    await message.answer(
        text="Теперь введите ссылку на событие.",
    )
    await state.set_state(FSMFillForm.fill_long_url)


@router.message(StateFilter(FSMFillForm.fill_long_url))
async def process_summary_sent(message: Message, state: FSMContext):
    await state.update_data(long_url=message.text)
    await message.answer(
        text="Теперь введите местоположение.",
    )
    await state.set_state(FSMFillForm.fill_location)


@router.message(StateFilter(FSMFillForm.fill_location))
async def process_location_sent(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer(
        text="Теперь введите описание события.",
    )

    await state.set_state(FSMFillForm.fill_description)


@router.message(StateFilter(FSMFillForm.fill_description))
async def process_description_sent(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        text=(
            "Теперь введите дату начала события "
            "в формате YYYY-MM-DD HH:MM:SS."
        ),
    )
    await state.set_state(FSMFillForm.fill_date_start)


@router.message(StateFilter(FSMFillForm.fill_date_start))
async def process_date_start_sent(message: Message, state: FSMContext):
    await state.update_data(date_start=message.text)
    await message.answer(
        text=(
            "Теперь введите дату окончания события "
            "в формате YYYY-MM-DD HH:MM:SS."
        ),
    )
    await state.set_state(FSMFillForm.fill_date_end)


@router.message(StateFilter(FSMFillForm.fill_date_end))
async def process_date_end_sent(message: Message, state: FSMContext):
    await state.update_data(date_end=message.text)

    data = await state.get_data()
    confirmation_message = (
        f"Подтвердите введенные данные:\n\n"
        f"Название: {data['summary']}\n"
        f"Ссылка на событие: {data['long_url']}\n"
        f"Местоположение: {data['location']}\n"
        f"Описание: {data['description']}\n"
        f"Начало: {data['date_start']}\n"
        f"Окончание: {data['date_end']}\n\n"
    )
    await message.answer(confirmation_message, reply_markup=confirm_keyboard())
    await state.set_state(FSMFillForm.confirmation)


@router.callback_query(StateFilter(FSMFillForm.confirmation))
async def process_confirmation(callback: CallbackQuery, state: FSMContext):
    if callback.data == "confirm":
        data = await state.get_data()
        await save_event_to_database(data)
        await state.clear()
        await callback.message.edit_text(
            "Событие сохранено в базе данных. Спасибо!"
        )
    elif callback.data == "cancel":
        await state.clear()
        await callback.message.edit_text(
            "Добавление события отменено. Выберите в меню или введите "
            "/add_event для создания нового события."
        )
    await callback.answer()
