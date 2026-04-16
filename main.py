import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from supabase import create_client, Client

# 1. СНАЧАЛА инициализируем FastAPI (это важно для Vercel)
app = FastAPI()

# Подтягиваем секретные ключи
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Инициализируем бота и базу
bot = Bot(token=TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.post("/api/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@dp.message()
async def cmd_start(message: types.Message):
    try:
        supabase.table("users").upsert({"telegram_id": message.from_user.id}).execute()
    except Exception as e:
        print(f"Ошибка БД: {e}")

    await message.answer(
        "Привет! Я готов отслеживать твои тренировки для набора массы.\n"
        "Жми кнопку ниже, чтобы открыть трекер!"
    )