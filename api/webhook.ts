import { waitUntil } from "@vercel/functions";
import { createClient } from "@supabase/supabase-js";
import { Bot, webhookCallback } from "grammy";

export const maxDuration = 30;

function getRequiredEnv(name: string): string {
  const value = process.env[name];

  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }

  return value;
}

const botToken = getRequiredEnv("BOT_TOKEN");
const supabaseUrl = getRequiredEnv("SUPABASE_URL");
const supabaseKey = getRequiredEnv("SUPABASE_KEY");
const telegramWebhookSecret = process.env.TELEGRAM_WEBHOOK_SECRET;

const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false,
  },
});

const bot = new Bot(botToken, {
  client: {
    // Отключаем webhook reply, чтобы HTTP-ответ Telegram не зависел от логики бота.
    canUseWebhookReply: () => false,
  },
});

bot.catch((error) => {
  console.error("grammy error:", error.error);
});

bot.command("start", async (ctx) => {
  const from = ctx.from;

  if (!from) {
    return;
  }

  // Upsert заменяет связку SELECT + INSERT: если пользователь уже есть, дубликат игнорируется.
  const { error } = await supabase.from("users").upsert(
    {
      telegram_id: from.id,
    },
    {
      onConflict: "telegram_id",
      ignoreDuplicates: true,
    },
  );

  if (error) {
    console.error("Supabase upsert error:", error);
  }

  await ctx.reply(
    [
      "Привет! Я Gym Tracker Bot.",
      "Я помогу хранить профиль и логи тренировок.",
      "Базовый backend на TypeScript уже подключен к Supabase и готов к дальнейшему расширению.",
    ].join("\n"),
  );
});

// Вебхук обрабатывается асинхронно: Telegram получает 200 OK сразу, а update дорабатывается в фоне.
const telegramWebhook = webhookCallback(bot, "std/http", {
  timeoutMilliseconds: Infinity,
  secretToken: telegramWebhookSecret,
});

export default async function handler(request: Request): Promise<Response> {
  if (request.method === "GET") {
    return Response.json({
      ok: true,
      service: "gym-tracker-bot-backend",
      timestamp: new Date().toISOString(),
    });
  }

  if (request.method !== "POST") {
    return new Response("Method Not Allowed", {
      status: 405,
      headers: {
        Allow: "GET, POST",
      },
    });
  }

  const backgroundTask = telegramWebhook(request.clone()).catch((error) => {
    console.error("Webhook processing error:", error);
  });

  waitUntil(backgroundTask);

  return new Response("OK", { status: 200 });
}
