import locale
from datetime import datetime
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from app.database import requests as rq
from app.keyboards import type_of_manic, send_number, confirmation, new_entry, yes_no, grey_button, grey_and_green_button, already_entry
from app.google_calendar.google_calendar_manager import calendar

locale.setlocale(locale.LC_TIME, 'uk_UA')

user = Router()


class Registration(StatesGroup):
    name = State()
    number = State()
    insta_name = State()


class Record(StatesGroup):
    date = State()
    id_event = State()
    time = State()
    category = State()
    comment = State()
    final = State()


@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await rq.add_user(message.from_user.id)
    if not user:
        await message.answer("Привіт 👋🏻\n\nВведи своє ім'я")
        await state.set_state(Registration.name)
    else:
        await message.answer("Ти можеш записатися на нігтики нажавши кнопку внизу)", reply_markup=new_entry)


@user.message(Registration.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Registration.number)
    await message.answer("Нажми на кнопку щоб поділитися свіїм номером телефону", reply_markup=send_number)


@user.message(Registration.number, F.contact)
async def get_number(message: Message, state: FSMContext):
    await state.update_data(number=message.contact.phone_number)
    await state.set_state(Registration.insta_name)
    await message.answer("Вкажи свій нік інстаграм", reply_markup=ReplyKeyboardRemove())


@user.message(Registration.insta_name)
async def get_insta_name(message: Message, state: FSMContext):
    await state.update_data(insta_name=message.text)
    user = await state.get_data()
    await rq.edit_user(message.from_user.id, user['name'], user['number'], user['insta_name'])
    await message.answer("Реєстрація пройшла успішно\n\nЩоб записатися на нігтики, жми кнопку)", reply_markup=new_entry)
    await state.clear()


@user.message(F.text == 'Відмінити запис')
async def cancel_record_question(message: Message):
    rec = await rq.get_user_rec(message.from_user.id)
    if rec:
        time = rec.date_time.strftime('%d.%m %A %H:%M')
        await message.answer(f"Записана на {time} \n\nточно відмінити запис?", reply_markup=yes_no)
    else:
        await message.answer("Щось пішло нетак", reply_markup=new_entry)


@user.message(F.text == 'Так')
async def cancel_record(message: Message):
    rec = await rq.get_user_rec(message.from_user.id)
    calendar.update_event_color(rec.id_event, "10", " ")
    await rq.delete_user_rec(message.from_user.id)
    await message.answer("Запис відмінено", reply_markup=new_entry)


@user.message(F.text == 'Ні')
async def new_record(message: Message, state: FSMContext):
    rec = await rq.get_user_rec(message.from_user.id)
    time = rec.date_time.strftime('%d.%m %A %H:%M')
    await message.answer(f"Ти вже записана на {time}", reply_markup=new_entry)


@user.message(F.text == 'Записатися')
async def new_record(message: Message, state: FSMContext):
    rec = await rq.get_user_rec(message.from_user.id)
    if not rec:
        await message.answer("Вибери що будемо робити (із запропонованого)", reply_markup=type_of_manic)
        await state.set_state(Record.category)
    else:
        time = rec.date_time.strftime('%d.%m %A %H:%M')
        await message.answer(f"ти вже записана на {time}", reply_markup=already_entry)


@user.message(F.text == 'перенарощення (450грн)')
@user.message(F.text == 'нарощення (400грн)')
async def get_date(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Вибери одну із запропонованих годин: ", reply_markup=await grey_button())
    await state.set_state(Record.date)


@user.message(F.text == 'зняття + чистка + укріплення (380/400грн)')
@user.message(F.text == 'зняття + чистка (250грн)')
async def get_date(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Вибери одну із запропонованих годин: ", reply_markup=await grey_and_green_button())
    await state.set_state(Record.date)


@user.callback_query(F.data.startswith('kl_'))
async def get_category(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(date=callback.data.split('_')[1])
    await state.update_data(time=callback.data.split('_')[1][11:16])
    await callback.message.answer(
        "Якщо ти бажаєш дизайн - напиши \"+\"  \nЯкщо ти бажаєш без дизайну - напиши \"-\"",
        reply_markup=ReplyKeyboardRemove())
    await state.set_state(Record.comment)


@user.message(Record.comment)
async def get_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    rec = await state.get_data()
    time = datetime.fromisoformat(rec['date']).strftime('%d.%m %A %H:%M')
    await message.answer(f"Твій запис на {time} ,\n\nБудемо робити {rec['category']}\n\nДизайн: {rec['comment']} ",
                         reply_markup=confirmation)
    await state.set_state(Record.final)


@user.message(Record.final)
async def get_final(message: Message, state: FSMContext):
    user_info = await rq.get_user(message.from_user.id)
    rec = await state.get_data()
    time = datetime.fromisoformat(rec['date']).strftime('%d.%m %A %H:%M')
    id_event = calendar.get_event_id_by_start_time(rec['date'].replace(' ', 'T'))
    if await rq.get_audit(rec['date']):
        await rq.add_rec_to_new_table(message.from_user.id, rec['date'], id_event)
        calendar.update_event_color(event_id=id_event,
                                    color_id="11",
                                    summary=f"{user_info.name}, +{user_info.number}, {user_info.insta_name} ,{message.from_user.id},\n\n тип робити {rec['category']}\n\nкоментар: {rec['comment']}")
        await message.answer(f"Чекатиму тебе {time}", reply_markup=new_entry)
        await state.clear()
    else:
        await message.answer("На жаль хтось записався швидше за тебе 😢\nСпробуй ще раз)", reply_markup=new_entry)
