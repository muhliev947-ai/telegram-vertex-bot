import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://telegram-vertex-bot.onrender.com

app = Flask(__name__)

MAIN_MENU = ReplyKeyboardMarkup(
    [["Оставить заявку", "Контакты"], ["О компании"]],
    resize_keyboard=True
)

# Telegram application
tg_app = Application.builder().token(TOKEN).build()


# ---------------- Telegram Handlers ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Я бот компании VERTEX.\nВыберите действие:",
        reply_markup=MAIN_MENU
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Оставить заявку":
        context.user_data["state"] = "name"
        await update.message.reply_text("Введите ваше имя:")
        return

    if context.user_data.get("state") == "name":
        context.user_data["name"] = text
        context.user_data["state"] = "phone"
        await update.message.reply_text("Введите номер телефона:")
        return

    if context.user_data.get("state") == "phone":
        context.user_data["phone"] = text

        name = context.user_data["name"]
        phone = context.user_data["phone"]

        await update.message.reply_text(
            f"Спасибо! Ваша заявка отправлена.\n\nИмя: {name}\nТелефон: {phone}",
            reply_markup=MAIN_MENU
        )

        if ADMIN_ID:
            await context.bot.send_message(
                chat_id=int(ADMIN_ID),
                text=f"📩 *Новая заявка*\n\n👤 Имя: {name}\n📞 Телефон: {phone}",
                parse_mode="Markdown"
            )

        context.user_data.clear()
        return

    if text == "Контакты":
        await update.message.reply_text("Наш телефон: +7 (999) 123‑45‑67")
        return

    if text == "О компании":
        await update.message.reply_text("VERTEX — инновационные решения для бизнеса.")
        return

    await update.message.reply_text(
        "Не понял команду. Выберите действие:",
        reply_markup=MAIN_MENU
    )


tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# ---------------- Flask Webhook ----------------

@app.post("/webhook")
def webhook():
    update = Update.de_json(request.json, tg_app.bot)
    tg_app.update_queue.put_nowait(update)
    return "OK", 200


@app.get("/")
def home():
    return "Bot is running!", 200


# ---------------- Startup ----------------

async def set_webhook():
    await tg_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")


if __name__ == "__main__":
    import asyncio

    print("Setting webhook...")
    asyncio.run(set_webhook())

    print("Starting Flask server...")
    port = int(os.environ.get("PORT", 10000))  # ВАЖНО!
    app.run(host="0.0.0.0", port=port)
