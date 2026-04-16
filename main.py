import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from supabase import create_client, Client

# Подтягиваем секретные ключи из переменных окружения Vercel
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Инициализируем бота и базу данных
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = FastAPI()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Этот эндпоинт будет принимать сигналы от Telegram
@app.post("/api/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    # Передаем полученное сообщение в aiogram
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}


# Реакция бота на команду /start
@dp.message()
async def cmd_start(message: types.Message):
    # При первом запуске добавляем Telegram ID пользователя в базу
    try:
        supabase.table("users").upsert({"telegram_id": message.from_user.id}).execute()
    except Exception as e:
        print(f"Ошибка БД: {e}")

    await message.answer(
        "Привет! Я готов отслеживать твои тренировки для набора массы.\n"
        "Жми кнопку ниже, чтобы открыть трекер!"
    )