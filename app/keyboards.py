from datetime import datetime
import locale
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.google_calendar.google_calendar_manager import calendar


locale.setlocale(locale.LC_TIME, 'uk_UA')

send_number = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Поділитися моїм номером телефону", request_contact=True)]], resize_keyboard=True)

new_entry = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Записатися")]], resize_keyboard=True)

already_entry = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Відмінити запис")]], resize_keyboard=True)

yes_no = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Так"), KeyboardButton(text="Ні")]], resize_keyboard=True)

type_of_manic = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="зняття + чистка + укріплення (380/400грн)")], [KeyboardButton(text="перенарощення (450грн)")], [KeyboardButton(text="нарощення (400грн)")], [KeyboardButton(text="зняття + чистка (250грн)")]], resize_keyboard=True)

confirmation = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Підтвердити")]], resize_keyboard=True)


async def grey_button():
    all_days = calendar.list_upcoming_events()
    keyboard = InlineKeyboardBuilder()
    for one_rec in all_days:

        if one_rec['colorId'] == "8":
            date_time = (datetime.fromisoformat(one_rec['start']['dateTime']))
            time = date_time.strftime('%d.%m %A %H:%M')
            keyboard.add(InlineKeyboardButton(text=f"{time}", callback_data=f"kl_{date_time}_f"))

    return keyboard.adjust(2).as_markup()


async def grey_and_green_button():
    all_days = calendar.list_upcoming_events()
    keyboard = InlineKeyboardBuilder()
    for one_rec in all_days:

        if (one_rec['colorId'] == "10") or (one_rec['colorId'] == "8"):
            date_time = (datetime.fromisoformat(one_rec['start']['dateTime']))
            time = date_time.strftime('%d.%m %A %H:%M')
            keyboard.add(InlineKeyboardButton(text=f"{time}", callback_data=f"kl_{date_time}_f"))

    return keyboard.adjust(2).as_markup()