import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

# Главное меню
MAIN_MENU = ReplyKeyboardMarkup(
    [["Оставить заявку", "Контакты"], ["О компании"]],
    resize_keyboard=True
)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Я бот компании VERTEX.\nВыберите действие:",
        reply_markup=MAIN_MENU
    )

# Обработка текста
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Оставить заявку":
        await update.message.reply_text("Введите ваше имя:")
        context.user_data["state"] = "name"

    elif context.user_data.get("state") == "name":
        context.user_data["name"] = text
        context.user_data["state"] = "phone"
        await update.message.reply_text("Введите номер телефона:")

    elif context.user_data.get("state") == "phone":
        context.user_data["phone"] = text
        context.user_data["state"] = "done"

        name = context.user_data["name"]
        phone = context.user_data["phone"]

        await update.message.reply_text(
            f"Спасибо! Ваша заявка отправлена.\n\nИмя: {name}\nТелефон: {phone}",
            reply_markup=MAIN_MENU
        )

        # Отправка админу
        ADMIN_ID = os.getenv("ADMIN_ID")
        if ADMIN_ID:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"Новая заявка:\nИмя: {name}\nТелефон: {phone}"
            )

        context.user_data.clear()

    elif text == "Контакты":
        await update.message.reply_text("Наш телефон: +7 (999) 123‑45‑67")

    elif text == "О компании":
        await update.message.reply_text("VERTEX — инновационные решения для бизнеса.")

    else:
        await update.message.reply_text("Не понял команду. Выберите действие:", reply_markup=MAIN_MENU)

# Главная функция
def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN не найден!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
