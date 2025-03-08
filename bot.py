import asyncio
import os
import csv
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

TOKEN = "7810956684:AAHoxj0tVxu2-yo3OsK_1tDuyT2V7y52sEU"
ADMIN_ID = 700721980

data_path = "data"
users_log = "users_log.csv"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Foydalanuvchi tanlovlarini saqlash
user_states = {}

# Tugmalar
years_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=str(year))] for year in [2024, 2025, 2026]] + [[KeyboardButton(text="⬅️ Назад")]],
    resize_keyboard=True
)

def get_months_keyboard():
    months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=month)] for month in months] + [[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True
    )
    return keyboard

def get_data_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Оклад"), KeyboardButton(text="⏳ Время полета")],
            [KeyboardButton(text="🧳 Pax"), KeyboardButton(text="🌙 Ночное время")],
            [KeyboardButton(text="💰 Общая сумма")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

# CSV'dan foydalanuvchi ID bo‘yicha ma'lumot olish
def get_csv_data(year, month, category, user_id):
    filename = os.path.join(data_path, year, month, f"{category}.csv")
    try:
        with open(filename, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader)  # Sarlavhani o‘tkazib yuboramiz
            user_data = [row for row in reader if row[0] == str(user_id)]
            if user_data:
                return "\n".join([", ".join(row) for row in user_data])
            else:
                return "❌ У вас нет данных в этом разделе."
    except FileNotFoundError:
        return "❌ Файл не найден."

# Yangi foydalanuvchini ro'yxatga olish
def log_user(user: types.User):
    if not os.path.exists(users_log):
        with open(users_log, "w", encoding="utf-8") as file:
            file.write("ID,Имя\n")
    with open(users_log, "r", encoding="utf-8") as file:
        users = file.readlines()
        if any(str(user.id) in line for line in users):
            return
    with open(users_log, "a", encoding="utf-8") as file:
        file.write(f"{user.id},{user.full_name}\n")

# /start komandasi
@dp.message(Command("start"))
async def start(message: types.Message):
    log_user(message.from_user)
    user_states[message.from_user.id] = {}
    await message.answer("👋 Привет! Выберите год:", reply_markup=years_keyboard)

# Yil tanlanganda
@dp.message(F.text.in_(["2024", "2025", "2026"]))
async def year_selected(message: types.Message):
    user_states[message.from_user.id] = {"year": message.text}
    await message.answer(f"📆 Вы выбрали {message.text} год. Теперь выберите месяц:", reply_markup=get_months_keyboard())

# Oy tanlanganda
@dp.message(F.text.in_([
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
]))
async def month_selected(message: types.Message):
    if message.from_user.id not in user_states or "year" not in user_states[message.from_user.id]:
        await message.answer("⚠️ Сначала выберите год.", reply_markup=years_keyboard)
        return
    user_states[message.from_user.id]["month"] = message.text
    await message.answer(f"📅 Вы выбрали {message.text}. Теперь выберите категорию:", reply_markup=get_data_keyboard())

# Tugma bosilganda CSV ma'lumot chiqarish
@dp.message(F.text.in_(["📊 Оклад", "⏳ Время полета", "🧳 Pax", "🌙 Ночное время", "💰 Общая сумма"]))
async def data_selected(message: types.Message):
    state = user_states.get(message.from_user.id, {})
    year = state.get("year", "")
    month = state.get("month", "")
    
    if not year or not month:
        await message.answer("⚠️ Сначала выберите год и месяц.", reply_markup=years_keyboard)
        return

    category_map = {
        "📊 Оклад": "oklad",
        "⏳ Время полета": "flight_time",
        "🧳 Pax": "pax",
        "🌙 Ночное время": "night_time",
        "💰 Общая сумма": "total"
    }

    category = category_map.get(message.text, "")
    data = get_csv_data(year, month, category, message.from_user.id)

    await message.answer(f"📂 Данные за {month} {year} - {message.text}:\n{data}")

# Ortga qaytish
@dp.message(F.text == "⬅️ Назад")
async def back(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_states:
        state = user_states[user_id]
        if "month" in state:
            del user_states[user_id]["month"]
            await message.answer("🔙 Вы вернулись назад. Выберите месяц:", reply_markup=get_months_keyboard())
        elif "year" in state:
            del user_states[user_id]
            await message.answer("🔙 Вы вернулись назад. Выберите год:", reply_markup=years_keyboard())
        else:
            await message.answer("🔙 Вы уже в главном меню.", reply_markup=years_keyboard())
    else:
        await message.answer("🔙 Вы уже в главном меню.", reply_markup=years_keyboard())

# Botni ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
