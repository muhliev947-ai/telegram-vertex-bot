#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime
import threading

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from flask import Flask, request

# ========================= CONFIG =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = 1371388170

PORT = int(os.getenv("PORT", 8080))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")   # ← Добавь этот URL в Variables на Railway

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found!")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========================= STATES & KEYBOARDS =========================
NAME, PROJECT, BUDGET, CONTACT, CONFIRM = range(5)

MAIN_MENU = ReplyKeyboardMarkup([
    ["🏢 О студии", "💼 Услуги и цены"],
    ["🖼 Портфолио", "❓ FAQ"],
    ["📞 Контакты", "✍️ Оставить заявку"]
], resize_keyboard=True)

CANCEL_MENU = ReplyKeyboardMarkup([["❌ Отменить"]], resize_keyboard=True)

# ========================= TEXTS =========================
START_TEXT = "Здравствуйте!\n\nДобро пожаловать в **VERTEX** — студию премиального digital-разработки."

ABOUT_TEXT = "🏢 **VERTEX** — цифровая студия полного цикла.\n\nМы создаём современные сайты, дизайн и системы автоматизации."

SERVICES_TEXT = (
    "💼 **Услуги и цены VERTEX**\n\n"
    "🖥 Веб-разработка — от 1500 ₽\n"
    "🎨 Дизайн — от 1000 ₽\n"
    "🤖 Telegram боты — от 1200 ₽\n\n"
    "Подробнее на сайте."
)

# Добавь остальные тексты (PORTFOLIO, FAQ, CONTACTS), если нужно

# ========================= SEND LEAD =========================
async def send_lead_to_admin(context, user_data, user):
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    msg = (
        f"🔥 <b>НОВАЯ ЗАЯВКА VERTEX</b>\n\n"
        f"👤 Имя: {user_data.get('name')}\n"
        f"📋 Проект: {user_data.get('project')}\n"
        f"💰 Бюджет: {user_data.get('budget')}\n"
        f"📞 Контакт: {user_data.get('contact')}\n"
        f"👤 @{user.username or '—'}\n"
        f"🆔 {user.id}\n"
        f"⏰ {timestamp}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Ошибка отправки заявки: {e}")

# ========================= HANDLERS =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(START_TEXT, reply_markup=MAIN_MENU, parse_mode='HTML')

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ["🏢 О студии", "О студии"]:
        await update.message.reply_text(ABOUT_TEXT, parse_mode='HTML')
    elif text in ["💼 Услуги и цены", "Услуги и цены"]:
        await update.message.reply_text(SERVICES_TEXT, parse_mode='HTML')
    elif text == "✍️ Оставить заявку":
        await update.message.reply_text(
            "<b>Шаг 1 из 4</b>\nВведите ваше имя:", 
            reply_markup=CANCEL_MENU, 
            parse_mode='HTML'
        )
        return NAME
    # Добавь остальные пункты меню по необходимости

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("<b>Шаг 2 из 4</b>\nОпишите ваш проект:", reply_markup=CANCEL_MENU, parse_mode='HTML')
    return PROJECT

async def project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['project'] = update.message.text
    await update.message.reply_text("<b>Шаг 3 из 4</b>\nУкажите бюджет:", reply_markup=CANCEL_MENU, parse_mode='HTML')
    return BUDGET

async def budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['budget'] = update.message.text
    await update.message.reply_text("<b>Шаг 4 из 4</b>\nОставьте контакт:", reply_markup=CANCEL_MENU, parse_mode='HTML')
    return CONTACT

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact'] = update.message.text
    preview = f"<b>Проверьте данные:</b>\n\n{context.user_data}"
    confirm_keyboard = ReplyKeyboardMarkup([["✅ Да, отправить"], ["❌ Отменить"]], resize_keyboard=True)
    await update.message.reply_text(preview, reply_markup=confirm_keyboard, parse_mode='HTML')
    return CONFIRM

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "да" in update.message.text.lower() or "✅" in update.message.text:
        await send_lead_to_admin(context, context.user_data, update.effective_user)
        await update.message.reply_text("✅ Заявка успешно отправлена!", reply_markup=MAIN_MENU, parse_mode='HTML')
    else:
        await update.message.reply_text("❌ Заявка отменена.", reply_markup=MAIN_MENU)
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Заявка отменена.", reply_markup=MAIN_MENU)
    context.user_data.clear()
    return ConversationHandler.END

# ========================= FLASK =========================
flask_app = Flask(__name__)

@flask_app.route('/')
def health():
    return "Bot is running on Railway!", 200

# ========================= MAIN =========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

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

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

    # Запуск Flask
    threading.Thread(target=lambda: flask_app.run(host='0.0.0.0', port=PORT), daemon=True).start()

    logger.info("✅ Бот успешно запущен!")

    if WEBHOOK_URL:
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path="webhook",
            webhook_url=f"{WEBHOOK_URL}/webhook"
        )
    else:
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
