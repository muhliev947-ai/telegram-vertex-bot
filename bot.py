#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from flask import Flask, request
import threading

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = 1371388170
SITE_URL = "https://next-site-self-two.vercel.app"
PORTFOLIO_URL = "https://next-site-self-two.vercel.app/portfolio"

# Railway даёт переменную PORT
PORT = int(os.getenv("PORT", 8080))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Добавь в Variables на Railway

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables!")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# =========================
# STATES & KEYBOARDS
# =========================
NAME, PROJECT, BUDGET, CONTACT, CONFIRM = range(5)

MAIN_MENU = ReplyKeyboardMarkup([
    ["🏢 О студии", "💼 Услуги и цены"],
    ["🖼 Портфолио", "❓ FAQ"],
    ["📞 Контакты", "✍️ Оставить заявку"]
], resize_keyboard=True)

CANCEL_MENU = ReplyKeyboardMarkup([["❌ Отменить"]], resize_keyboard=True)

# =========================
# TEXTS (оставил без изменений)
# =========================
START_TEXT = "Здравствуйте!\n\nДобро пожаловать в **VERTEX** — студию премиального digital-разработки."

# ... (все остальные тексты ABOUT_TEXT, SERVICES_TEXT и т.д. оставь как были)

# =========================
# SEND LEAD
# =========================
async def send_lead_to_admin(context, user_data, user):
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    msg = (
        f"🔥 <b>НОВАЯ ЗАЯВКА VERTEX</b>\n\n"
        f"👤 Имя: {user_data['name']}\n"
        f"📋 Проект: {user_data.get('project', '-')}\n"
        f"💰 Бюджет: {user_data.get('budget', '-')}\n"
        f"📞 Контакт: {user_data.get('contact', '-')}\n"
        f"👤 @{user.username or '—'}\n"
        f"🆔 {user.id}\n"
        f"⏰ {timestamp}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, parse_mode='HTML')
        logger.info("✅ Заявка отправлена админу")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки: {e}")

# =========================
# HANDLERS (оставил почти без изменений)
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(START_TEXT, reply_markup=MAIN_MENU, parse_mode='HTML')

# ... (все твои handlers: menu_handler, name, project, budget, contact, confirm, cancel — оставь как были)

# =========================
# FLASK WEB SERVER (для Railway)
# =========================
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "VERTEX Bot is running!", 200

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        update = Update.de_json(request.get_json(), application.bot)
        application.update_queue.put(update)
        return 'OK', 200
    return 'Method not allowed', 405

# =========================
# MAIN
# =========================
application = None

def run_flask():
    flask_app.run(host='0.0.0.0', port=PORT)

def main():
    global application
    
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("✍️ Оставить заявку"), menu_handler)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, project)],
            BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, budget)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[MessageHandler(filters.Regex("❌ Отменить"), cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

    # Запускаем Flask в отдельном потоке
    threading.Thread(target=run_flask, daemon=True).start()

    logger.info("✅ VERTEX Bot запущен!")

    if WEBHOOK_URL:
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="webhook",
            webhook_url=f"{WEBHOOK_URL}/webhook"
        )
    else:
        # Fallback на polling (если webhook не настроен)
        logger.warning("WEBHOOK_URL не указан → используем polling")
        application.run_polling()

if __name__ == "__main__":
    main()
