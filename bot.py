import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Получаем токен и ID админа из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Главное меню
MAIN_MENU = ReplyKeyboardMarkup(
    [["Оставить заявку", "Контакты"], ["О компании"]],
    resize_keyboard=True
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здравствуйте! Я бот компании VERTEX.\nВыберите действие:",
        reply_markup=MAIN_MENU
    )

# Обработка всех текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Пользователь нажал "Оставить заявку"
    if text == "Оставить заявку":
        await update.message.reply_text("Введите ваше имя:")
        context.user_data["state"] = "name"
        return

    # Шаг 1 — имя
    if context.user_data.get("state") == "name":
        context.user_data["name"] = text
        context.user_data["state"] = "phone"
        await update.message.reply_text("Введите номер телефона:")
        return

    # Шаг 2 — телефон
    if context.user_data.get("state") == "phone":
        context.user_data["phone"] = text
        name = context.user_data["name"]
        phone = context.user_data["phone"]

        # Сообщение пользователю
        await update.message.reply_text(
            f"Спасибо! Ваша заявка отправлена.\n\nИмя: {name}\nТелефон: {phone}",
            reply_markup=MAIN_MENU
        )

        # Отправка админу
        if ADMIN_ID:
            await context.bot.send_message(
                chat_id=int(ADMIN_ID),
                text=f"📩 *Новая заявка*\n\n👤 Имя: {name}\n📞 Телефон: {phone}",
                parse_mode="Markdown"
            )

        context.user_data.clear()
        return

    # Контакты
    if text == "Контакты":
        await update.message.reply_text("Наш телефон: +7 (999) 123‑45‑67")
        return

    # О компании
    if text == "О компании":
        await update.message.reply_text("VERTEX — инновационные решения для бизнеса.")
        return

    # Если бот не понял
    await update.message.reply_text(
        "Не понял команду. Выберите действие:",
        reply_markup=MAIN_MENU
    )

# Главная функция
def main():
    if not TOKEN:
        raise RuntimeError("❌ BOT_TOKEN не найден! Добавьте его в переменные окружения.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # ВАЖНО: run_polling() работает на Python 3.14
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
