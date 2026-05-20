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

YOUR_CHAT_ID = 1371388170  # Твой Chat ID
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

# ==================== КНОПКИ И ТЕКСТЫ (УПРОЩЁННО ДЛЯ КРАТКОСТИ) ====================
BTN_ABOUT, BTN_SERVICES, BTN_PORTFOLIO, BTN_CONTACTS, BTN_FAQ, BTN_ORDER, BTN_CALC, BTN_BACK_TO_MENU = "📖 О нас", "💰 Услуги", "🖼 Портфолио", "📞 Контакты", "❓ FAQ", "📝 Оставить заявку", "🧮 Калькулятор цен", "🔙 В главное меню"
TEXT_SERVICES = "💎 УСЛУГИ И ЦЕНЫ\n• Landing page — от 1500 ₽\n• Корпоративный сайт — от 3500 ₽\n• Интернет-магазин — от 6000 ₽\n• SaaS / Дашборд — от 9000 ₽\n• Мобильное приложение — от 8000 ₽\n• Telegram бот — от 1200 ₽"
TEXT_START = "👋 Добро пожаловать в VERTEX!\nВыберите раздел в меню ниже 👇"
TEXT_ORDER_REQUEST = "📝 ОСТАВИТЬ ЗАЯВКУ\n\n1️⃣ Ваше имя:"
TEXT_AFTER_NAME, TEXT_AFTER_PROJECT, TEXT_AFTER_BUDGET = "2️⃣ Что нужно разработать?", "3️⃣ Ваш бюджет?", "4️⃣ Ваш телефон:"
TEXT_THANK_YOU = "✅ Заявка принята! Мы свяжемся с вами в течение 15 минут."
TEXT_ABOUT = "🏢 КОМПАНИЯ VERTEX\nМы создаём сайты, приложения, ботов и дизайн."

def get_main_keyboard():
    return ReplyKeyboardMarkup([[BTN_ABOUT, BTN_SERVICES], [BTN_PORTFOLIO, BTN_CONTACTS], [BTN_FAQ, BTN_CALC], [BTN_ORDER]], resize_keyboard=True)
def get_back_keyboard():
    return ReplyKeyboardMarkup([[BTN_BACK_TO_MENU]], resize_keyboard=True)
def get_calculator_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("📄 Landing page", callback_data="price_landing")], [InlineKeyboardButton("🏢 Корпоративный сайт", callback_data="price_corporate")], [InlineKeyboardButton("🛒 Интернет-магазин", callback_data="price_shop")], [InlineKeyboardButton("📱 Мобильное приложение", callback_data="price_app")], [InlineKeyboardButton("🤖 Telegram бот", callback_data="price_bot")]])
def get_portfolio_inline_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Перейти на сайт", url=PORTFOLIO_URL)]])

# ==================== ОБРАБОТЧИКИ ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXT_START, reply_markup=get_main_keyboard())
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, user = update.message.text, update.effective_user
    if context.user_data.get('order_step'):
        step = context.user_data.get('order_step')
        if step == 'name':
            context.user_data['name'], context.user_data['order_step'] = text, 'project'
            await update.message.reply_text(TEXT_AFTER_NAME)
        elif step == 'project':
            context.user_data['project'], context.user_data['order_step'] = text, 'budget'
            await update.message.reply_text(TEXT_AFTER_PROJECT)
        elif step == 'budget':
            context.user_data['budget'], context.user_data['order_step'] = text, 'phone'
            await update.message.reply_text(TEXT_AFTER_BUDGET)
        elif step == 'phone':
            context.user_data['phone'] = text
            lead_info = f"🆕 ЗАЯВКА!\n👤 {clean_text(context.user_data.get('name'))}\n📋 {clean_text(context.user_data.get('project'))}\n💰 {clean_text(context.user_data.get('budget'))}\n📞 {clean_text(context.user_data.get('phone'))}\n🆔 @{user.username or 'нет'}\n🆔 {user.id}\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            logger.info(f"Заявка: {lead_info}")
            try:
                await context.bot.send_message(chat_id=YOUR_CHAT_ID, text=lead_info)
            except Exception as e:
                logger.error(f"Ошибка отправки: {e}")
            await update.message.reply_text(TEXT_THANK_YOU, reply_markup=get_portfolio_inline_keyboard())
            context.user_data.clear()
        return
    # Обработка кнопок (упрощенно для краткости)
    await update.message.reply_text("✅ Работаю!", reply_markup=get_main_keyboard())
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("✅ Цена уточнена. Оставьте заявку через меню.", reply_markup=get_calculator_keyboard())

# ==================== ЗАПУСК ====================
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # Запускаем веб-сервер Flask для health check
    flask_app = Flask(__name__)
    @flask_app.route('/')
    def health():
        return "Bot is running", 200
    @flask_app.route(f'/webhook/{TOKEN}', methods=['POST'])
    async def webhook():
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
        return "ok", 200

    # Запускаем Flask в фоновом потоке
    import threading
    threading.Thread(target=lambda: flask_app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)).start()

    # Устанавливаем вебхук и запускаем бота
    application.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook/{TOKEN}")

if __name__ == "__main__":
    main()
