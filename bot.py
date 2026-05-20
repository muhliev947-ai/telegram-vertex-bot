#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import re
from datetime import datetime
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ==================== КОНФИГУРАЦИЯ ====================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не задан!")

YOUR_CHAT_ID = 1371388170  # Куда отправлять заявки
PORTFOLIO_URL = "https://next-site-self-two.vercel.app"

# ==================== ЛОГИРОВАНИЕ ====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def clean_text(text):
    if not text:
        return "не указан"
    cleaned = re.sub(r'[^\w\s@\.\+\-\_\,\(\)]', '', str(text))
    return cleaned.strip() or "не указан"

# ==================== КНОПКИ ====================
BTN_ABOUT = "📖 О нас"
BTN_SERVICES = "💰 Услуги"
BTN_PORTFOLIO = "🖼 Портфолио"
BTN_CONTACTS = "📞 Контакты"
BTN_FAQ = "❓ FAQ"
BTN_ORDER = "📝 Оставить заявку"
BTN_CALC = "🧮 Калькулятор цен"
BTN_BACK = "🔙 В главное меню"

# ==================== ТЕКСТЫ ====================
TEXT_START = "👋 Добро пожаловать в VERTEX!\nВыберите раздел в меню ниже 👇"
TEXT_ABOUT = "🏢 КОМПАНИЯ VERTEX\nМы создаём сайты, приложения, ботов и дизайн."
TEXT_SERVICES = (
    "💎 УСЛУГИ И ЦЕНЫ\n"
    "• Landing page — от 1500 ₽\n"
    "• Корпоративный сайт — от 3500 ₽\n"
    "• Интернет-магазин — от 6000 ₽\n"
    "• SaaS / Дашборд — от 9000 ₽\n"
    "• Мобильное приложение — от 8000 ₽\n"
    "• Telegram бот — от 1200 ₽"
)

TEXT_ORDER_1 = "📝 ОСТАВИТЬ ЗАЯВКУ\n\n1️⃣ Ваше имя:"
TEXT_ORDER_2 = "2️⃣ Что нужно разработать?"
TEXT_ORDER_3 = "3️⃣ Ваш бюджет?"
TEXT_ORDER_4 = "4️⃣ Как с вами связаться? (телефон, @username или email)"
TEXT_THANK_YOU = "✅ Заявка принята! Мы свяжемся с вами в течение 15 минут."

# ==================== КЛАВИАТУРЫ ====================
def main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [BTN_ABOUT, BTN_SERVICES],
            [BTN_PORTFOLIO, BTN_CONTACTS],
            [BTN_FAQ, BTN_CALC],
            [BTN_ORDER]
        ],
        resize_keyboard=True
    )

def calc_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Landing page", callback_data="price_landing")],
        [InlineKeyboardButton("🏢 Корпоративный сайт", callback_data="price_corporate")],
        [InlineKeyboardButton("🛒 Интернет-магазин", callback_data="price_shop")],
        [InlineKeyboardButton("📱 Мобильное приложение", callback_data="price_app")],
        [InlineKeyboardButton("🤖 Telegram бот", callback_data="price_bot")]
    ])

def portfolio_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Перейти на сайт", url=PORTFOLIO_URL)]
    ])

# ==================== ОБРАБОТЧИКИ ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXT_START, reply_markup=main_keyboard())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # ---------- СЦЕНАРИЙ ЗАЯВКИ ----------
    if context.user_data.get("order_step"):
        step = context.user_data["order_step"]

        if step == "name":
            context.user_data["name"] = text
            context.user_data["order_step"] = "project"
            await update.message.reply_text(TEXT_ORDER_2)
            return

        if step == "project":
            context.user_data["project"] = text
            context.user_data["order_step"] = "budget"
            await update.message.reply_text(TEXT_ORDER_3)
            return

        if step == "budget":
            context.user_data["budget"] = text
            context.user_data["order_step"] = "contact"
            await update.message.reply_text(TEXT_ORDER_4)
            return

        if step == "contact":
            context.user_data["contact"] = text

            lead = (
                "🆕 НОВАЯ ЗАЯВКА!\n\n"
                f"👤 Имя: {clean_text(context.user_data['name'])}\n"
                f"📋 Проект: {clean_text(context.user_data['project'])}\n"
                f"💰 Бюджет: {clean_text(context.user_data['budget'])}\n"
                f"📞 Контакт: {clean_text(context.user_data['contact'])}\n"
                f"🆔 Telegram: @{user.username or 'нет'}\n"
                f"🆔 ID: {user.id}\n"
                f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # Отправляем заявку тебе
            await context.bot.send_message(chat_id=YOUR_CHAT_ID, text=lead)

            # Ответ пользователю
            await update.message.reply_text(TEXT_THANK_YOU, reply_markup=portfolio_keyboard())

            context.user_data.clear()
            return

    # ---------- МЕНЮ ----------
    if text == BTN_ABOUT:
        await update.message.reply_text(TEXT_ABOUT, reply_markup=main_keyboard())
        return

    if text == BTN_SERVICES:
        await update.message.reply_text(TEXT_SERVICES, reply_markup=main_keyboard())
        return

    if text == BTN_PORTFOLIO:
        await update.message.reply_text("🖼 Наше портфолио:", reply_markup=portfolio_keyboard())
        return

    if text == BTN_CONTACTS:
        await update.message.reply_text("📞 Контакты:\nTelegram: @vertex_dev\nEmail: info@vertex.com", reply_markup=main_keyboard())
        return

    if text == BTN_FAQ:
        await update.message.reply_text("❓ Частые вопросы:\n• Сроки?\n• Стоимость?\n• Этапы работы?", reply_markup=main_keyboard())
        return

    if text == BTN_CALC:
        await update.message.reply_text("🧮 Выберите тип проекта:", reply_markup=calc_keyboard())
        return

    if text == BTN_ORDER:
        context.user_data["order_step"] = "name"
        await update.message.reply_text(TEXT_ORDER_1)
        return

    # ---------- ФОЛБЭК ----------
    await update.message.reply_text("🤖 Я вас понял! Выберите действие в меню ниже 👇", reply_markup=main_keyboard())

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "💡 Цена зависит от деталей проекта.\nОставьте заявку через меню.",
        reply_markup=calc_keyboard()
    )

# ==================== ЗАПУСК ====================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    app.run_polling()

if __name__ == "__main__":
    main()
