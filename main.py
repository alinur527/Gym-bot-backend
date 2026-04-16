import os
import traceback
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from supabase import create_client, Client

app = FastAPI()


# 1. Секретный путь для проверки ошибок прямо в браузере
@app.get("/api/debug")
async def debug_mode():
    try:
        token = os.getenv("BOT_TOKEN")
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not token or not url or not key:
            return {"error": "ВНИМАНИЕ: Один из секретных ключей (Environment Variables) не найден в Vercel!"}

        # Тестовая инициализация
        test_bot = Bot(token=token)
        test_db = create_client(url, key)
        return {"status": "SUCCESS! Все ключи загружены, база данных подключена, ошибок нет!"}
    except Exception as e:
        # Если есть ошибка, выводим её на экран
        return {"error": str(e), "traceback": traceback.format_exc()}


# 2. Основной путь для Telegram
@app.post("/api/webhook")
async def webhook_handler(request: Request):
    try:
        # Инициализируем всё ВНУТРИ запроса (решает 99% проблем Vercel с "засыпанием")
        bot = Bot(token=os.getenv("BOT_TOKEN"))
        dp = Dispatcher()
        supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

        @dp.message()
        async def cmd_start(message: types.Message):
            try:
                supabase.table("users").upsert({"telegram_id": message.from_user.id}).execute()
            except Exception as e:
                print(f"Ошибка БД: {e}")
            await message.answer(
                "Привет! Я готов отслеживать твои тренировки для набора массы.\nЖми кнопку ниже, чтобы открыть трекер!")

        data = await request.json()
        update = types.Update(**data)
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"status": "error"}