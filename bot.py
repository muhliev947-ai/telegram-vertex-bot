#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import re
from datetime import datetime
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# ==================== КОНФИГУРАЦИЯ ====================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не задан!")

YOUR_CHAT_ID = 1371388170
PORT = int(os.environ.get('PORT', 10000))
PORTFOLIO_URL = "https://next-site-self-two.vercel.app"

# ==================== ЛОГИРОВАНИЕ ====================
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text):
    if not text:
        return "не указан"
    cleaned = re.sub(r'[^\w\s@\.\+\-\_\,\(\)]', '', str(text))
    return cleaned.strip() or "не указан"

# ==================== КНОПКИ И ТЕКСТЫ ====================
BTN_ABOUT = "📖 О нас"
BTN_SERVICES = "💰 Услуги"
BTN_PORTFOLIO = "🖼 Портфолио"
BTN_CONTACTS = "📞 Контакты"
BTN_FAQ = "❓ FAQ"
BTN_ORDER = "📝 Оставить заявку"
BTN_CALC = "🧮 Калькулятор цен"
BTN_BACK_TO_MENU = "🔙 В главное меню"

TEXT_SERVICES = (
    "💎 УСЛУГИ И ЦЕНЫ\n"
    "• Landing page — от 1500 ₽\n"
    "• Корпоративный сайт — от 3500 ₽\n"
    "• Интернет-магазин — от 6000 ₽\n"
    "• SaaS / Дашборд — от 9000 ₽\n"
    "• Мобильное приложение — от 8000 ₽\n"
    "• Telegram бот — от 1200 ₽"
)
TEXT_START = "👋 Добро пожаловать в VERTEX!\nВыберите раздел в меню ниже 👇"
TEXT_ORDER_REQUEST = "📝 ОСТАВИТЬ ЗАЯВКУ\n\n1️⃣ Ваше имя:"
TEXT_AFTER_NAME = "2️⃣ Что нужно разработать? (сайт, магазин, приложение, бот)"
TEXT_AFTER_PROJECT = "3️⃣ Ваш бюджет? (примерная сумма)"
TEXT_AFTER_BUDGET = "4️⃣ Ваш телефон для связи:"
TEXT_THANK_YOU = "✅ Заявка принята! Мы свяжемся с вами в течение 15 минут."

def get_main_keyboard():
    return ReplyKeyboardMarkup([
        [BTN_ABOUT, BTN_SERVICES],
        [BTN_PORTFOLIO, BTN_CONTACTS],
        [BTN_FAQ, BTN_CALC],
        [BTN_ORDER]
    ], resize_keyboard=True)

def get_back_keyboard():
    return ReplyKeyboardMarkup([[BTN_BACK_TO_MENU]], resize_keyboard=True)

def get_calculator_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Landing page", callback_data="price_landing")],
        [InlineKeyboardButton("🏢 Корпоративный сайт", callback_data="price_corporate")],
        [InlineKeyboardButton("🛒 Интернет-магазин", callback_data="price_shop")],
        [InlineKeyboardButton("📱 Мобильное приложение", callback_data="price_app")],
        [InlineKeyboardButton("🤖 Telegram бот", callback_data="price_bot")]
    ])

def get_portfolio_inline_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Перейти на сайт", url=PORTFOLIO_URL)]
    ])

# ==================== ОБРАБОТЧИКИ ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXT_START, reply_markup=get_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Помощь: /start - главное меню, /help - эта справка", reply_markup=get_back_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if context.user_data.get('order_step'):
        step = context.user_data.get('order_step')
        if step == 'name':
            context.user_data['name'] = text
            context.user_data['order_step'] = 'project'
            await update.message.reply_text(TEXT_AFTER_NAME)
        elif step == 'project':
            context.user_data['project'] = text
            context.user_data['order_step'] = 'budget'
            await update.message.reply_text(TEXT_AFTER_PROJECT)
        elif step == 'budget':
            context.user_data['budget'] = text
            context.user_data['order_step'] = 'phone'
            await update.message.reply_text(TEXT_AFTER_BUDGET)
        elif step == 'phone':
            context.user_data['phone'] = text
            lead_info = (
                f"🆕 НОВАЯ ЗАЯВКА!\n\n"
                f"👤 Имя: {clean_text(context.user_data.get('name'))}\n"
                f"📋 Проект: {clean_text(context.user_data.get('project'))}\n"
                f"💰 Бюджет: {clean_text(context.user_data.get('budget'))}\n"
                f"📞 Телефон: {clean_text(context.user_data.get('phone'))}\n"
                f"🆔 Telegram: @{user.username or 'нет'}\n"
                f"🆔 User ID: {user.id}\n"
                f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            logger.info(f"Заявка: {lead_info}")
            try:
                await context.bot.send_message(chat_id=YOUR_CHAT_ID, text=lead_info)
            except Exception as e:
                logger.error(f"Ошибка отправки: {e}")
            await update.message.reply_text(TEXT_THANK_YOU, reply_markup=get_portfolio_inline_keyboard())
            context.user_data.clear()
        return

    # Обработка кнопок
    if text == BTN_ABOUT:
        await update.message.reply_text("🏢 КОМПАНИЯ VERTEX\nМы создаём сайты, приложения, ботов и дизайн.", reply_markup=get_back_keyboard())
    elif text == BTN_SERVICES:
        await update.message.reply_text(TEXT_SERVICES, reply_markup=get_back_keyboard())
    elif text == BTN_PORTFOLIO:
        await update.message.reply_text("🖼 Наше портфолио на сайте:", reply_markup=get_portfolio_inline_keyboard())
    elif text == BTN_CONTACTS:
        await update.message.reply_text("📞 Свяжитесь с нами:\n📧 Email: vertexsite07@gmail.com\n📱 Telegram: @Fulstak_raz", reply_markup=get_back_keyboard())
    elif text == BTN_FAQ:
        await update.message.reply_text("❓ Частые вопросы:\nСроки: от 3 дней\nОплата: предоплата 30-50%\nГарантия: 3 месяца", reply_markup=get_back_keyboard())
    elif text == BTN_CALC:
        await update.message.reply_text("🧮 КАЛЬКУЛЯТОР ЦЕН\nВыберите тип проекта:", reply_markup=get_calculator_keyboard())
    elif text == BTN_ORDER:
        context.user_data['order_step'] = 'name'
        await update.message.reply_text(TEXT_ORDER_REQUEST, reply_markup=ReplyKeyboardMarkup([[BTN_BACK_TO_MENU]], resize_keyboard=True))
    elif text == BTN_BACK_TO_MENU:
        context.user_data.clear()
        await update.message.reply_text("🔙 Главное меню:", reply_markup=get_main_keyboard())
    else:
        await update.message.reply_text("❓ Пожалуйста, выберите пункт из меню.", reply_markup=get_main_keyboard())

async def handle_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prices = {
        "price_landing": "📄 Landing page\n💰 от 1500 ₽\n📅 3-5 дней",
        "price_corporate": "🏢 Корпоративный сайт\n💰 от 3500 ₽\n📅 7-10 дней",
        "price_shop": "🛒 Интернет-магазин\n💰 от 6000 ₽\n📅 14-21 день",
        "price_app": "📱 Мобильное приложение\n💰 от 8000 ₽\n📅 от 30 дней",
        "price_bot": "🤖 Telegram бот\n💰 от 1200 ₽\n📅 3-7 дней",
    }
    text = prices.get(query.data, "Выберите проект из списка")
    await query.edit_message_text(
        text=f"{text}\n\nДля точного расчёта — оставьте заявку через меню.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Оставить заявку", callback_data="order")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_to_calc")]
        ])
    )

async def handle_back_to_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🧮 КАЛЬКУЛЯТОР ЦЕН\nВыберите тип проекта:", reply_markup=get_calculator_keyboard())

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data.startswith("price_"):
        await handle_calculator(update, context)
    elif query.data == "back_to_calc":
        await handle_back_to_calc(update, context)
    elif query.data == "order":
        await query.answer()
        await query.message.reply_text("📝 Оставьте заявку через главное меню — кнопка 'Оставить заявку'")
    else:
        await query.answer()

# ==================== ЗАПУСК ====================
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # Flask для health check
    flask_app = Flask(__name__)
    @flask_app.route('/')
    def health():
        return "Bot is running", 200
    @flask_app.route(f'/webhook/{TOKEN}', methods=['POST'])
    async def webhook():
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
        return "ok", 200

    import threading
    threading.Thread(target=lambda: flask_app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)).start()

    # Запуск бота в режиме webhook
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook/{TOKEN}"
    application.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=webhook_url)

if __name__ == "__main__":
    main()
