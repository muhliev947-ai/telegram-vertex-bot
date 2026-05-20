#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram бот для компании VERTEX
Услуги: разработка сайтов, приложений, ботов, дизайн
"""

import logging
import os
from datetime import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ==================== КОНФИГУРАЦИЯ ====================

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не задан!")

# Второй бот для отправки уведомлений (Vertex_site_bot)
NOTIFIER_TOKEN = os.getenv("NOTIFIER_BOT_TOKEN")
notifier_bot = None

# Твой личный Chat ID (куда отправлять заявки)
# Узнать можно: написать @Vertex_site_bot → https://api.telegram.org/bot<TOKEN>/getUpdates
YOUR_CHAT_ID = 1371388170  # ← ЗАМЕНИ НА СВОЙ CHAT_ID

PORTFOLIO_URL = "https://next-site-self-two.vercel.app"

# ==================== ТЕКСТЫ КНОПОК ====================

BTN_ABOUT = "📖 О нас"
BTN_SERVICES = "💰 Услуги"
BTN_PORTFOLIO = "🖼 Портфолио"
BTN_CONTACTS = "📞 Контакты"
BTN_FAQ = "❓ FAQ"
BTN_ORDER = "📝 Оставить заявку"
BTN_CALC = "🧮 Калькулятор цен"
BTN_BACK_TO_MENU = "🔙 В главное меню"
BTN_SEND_CONTACT = "📲 Отправить контакт"

# ==================== ТЕКСТОВЫЕ БЛОКИ ====================

TEXT_ABOUT = (
    "🏢 КОМПАНИЯ VERTEX\n\n"
    "Мы — команда профессионалов, специализирующаяся на разработке "
    "цифровых продуктов под ключ.\n\n"
    "Чем мы занимаемся:\n"
    "• Разработка сайтов\n"
    "• Интернет-магазины\n"
    "• Мобильные приложения\n"
    "• SaaS платформы\n"
    "• UI/UX дизайн\n"
    "• Telegram боты\n\n"
    "Почему мы:\n"
    "• Цены ниже рынка при высоком качестве\n"
    "• Соблюдение сроков\n"
    "• Техподдержка после сдачи проекта"
)

TEXT_SERVICES = (
    "💎 НАШИ УСЛУГИ И ЦЕНЫ\n\n"
    "• Landing page — от 1500 ₽\n"
    "• Корпоративный сайт — от 3500 ₽\n"
    "• Интернет-магазин — от 6000 ₽\n"
    "• SaaS / Дашборд — от 9000 ₽\n"
    "• Мобильное приложение — от 8000 ₽\n"
    "• Telegram бот — от 1200 ₽\n\n"
    "⚡️ Акция: Скидка 15% при заказе сайта + бота!\n\n"
    "📞 Для точного расчёта — свяжитесь с нами."
)

TEXT_CONTACTS = (
    "📞 СВЯЖИТЕСЬ С НАМИ\n\n"
    "✉️ Email: vertexsite07@gmail.com\n"
    "📱 Telegram: @Fulstak_raz\n"
    "💬 WhatsApp: +7 928 092-2250\n\n"
    "🕐 Режим работы: 10:00 — 20:00 МСК\n\n"
    "👉 Нажмите на ссылку ниже, чтобы написать нам в Telegram!"
)

TEXT_FAQ = (
    "❓ ЧАСТЫЕ ВОПРОСЫ\n\n"
    "📅 Сроки разработки:\n"
    "• Landing page — 3-5 дней\n"
    "• Корпоративный сайт — 7-10 дней\n"
    "• Интернет-магазин — 14-21 день\n"
    "• Мобильное приложение — от 30 дней\n\n"
    "💰 Оплата:\n"
    "• Предоплата 30-50%\n"
    "• Можно поэтапно\n"
    "• Безналичный расчёт\n\n"
    "🛡️ Гарантия:\n"
    "• 3 месяца бесплатной поддержки\n"
    "• Исправление ошибок за наш счёт\n\n"
    "📞 Другие вопросы — напишите нам: @Fulstak_raz"
)

TEXT_ORDER_REQUEST = (
    "📝 ОСТАВИТЬ ЗАЯВКУ\n\n"
    "Ответьте на несколько вопросов, и мы свяжемся с вами.\n\n"
    "1️⃣ Напишите ваше имя:"
)

TEXT_AFTER_NAME = "2️⃣ Что нужно разработать? (сайт, магазин, приложение, бот)"
TEXT_AFTER_PROJECT = "3️⃣ Какой у вас бюджет? (примерная сумма)"
TEXT_AFTER_BUDGET = "4️⃣ Напишите ваш номер телефона для связи:"

TEXT_THANK_YOU = (
    "✅ СПАСИБО ЗА ЗАЯВКУ!\n\n"
    "Мы получили ваши данные и свяжемся с вами в течение 15 минут.\n\n"
    "А пока можете посмотреть наше портфолио на сайте 👇"
)

TEXT_START = (
    "👋 Добро пожаловать в VERTEX!\n\n"
    "Мы создаём сайты, приложения, ботов и дизайн.\n\n"
    "📌 Что вы хотите узнать?\n\n"
    "• О нас — кто мы и чем занимаемся\n"
    "• Услуги — цены на наши работы\n"
    "• Портфолио — наши проекты\n"
    "• Контакты — как с нами связаться\n"
    "• FAQ — частые вопросы\n\n"
    "Выберите раздел в меню ниже 👇"
)

TEXT_HELP = (
    "ℹ️ СПРАВКА ПО БОТУ\n\n"
    "/start — главное меню\n"
    "/help — эта справка\n\n"
    "Кнопки меню:\n"
    "📖 О нас — информация о компании\n"
    "💰 Услуги — прайс-лист\n"
    "🖼 Портфолио — ссылка на наши работы\n"
    "📞 Контакты — способы связи\n"
    "❓ FAQ — частые вопросы\n\n"
    "📝 Оставить заявку — заполните форму, и мы перезвоним"
)

# ==================== ЛОГИРОВАНИЕ ====================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ==================== КЛАВИАТУРЫ ====================

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [BTN_ABOUT, BTN_SERVICES],
            [BTN_PORTFOLIO, BTN_CONTACTS],
            [BTN_FAQ, BTN_CALC],
            [BTN_ORDER],
        ],
        resize_keyboard=True,
    )


def get_back_keyboard():
    return ReplyKeyboardMarkup(
        [[BTN_BACK_TO_MENU]],
        resize_keyboard=True,
    )


def get_contact_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_SEND_CONTACT, request_contact=True)]],
        resize_keyboard=True,
    )


def get_calculator_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Landing page", callback_data="price_landing")],
        [InlineKeyboardButton("🏢 Корпоративный сайт", callback_data="price_corporate")],
        [InlineKeyboardButton("🛒 Интернет-магазин", callback_data="price_shop")],
        [InlineKeyboardButton("📱 Мобильное приложение", callback_data="price_app")],
        [InlineKeyboardButton("🤖 Telegram бот", callback_data="price_bot")],
    ])


def get_portfolio_inline_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Перейти на сайт", url=PORTFOLIO_URL)],
        [InlineKeyboardButton("📝 Оставить заявку", callback_data="order")],
    ])


# ==================== ОБРАБОТЧИКИ КОМАНД ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Пользователь {user.id} (@{user.username}) запустил бота")
    await update.message.reply_text(TEXT_START, reply_markup=get_main_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXT_HELP, reply_markup=get_back_keyboard())


# ==================== ОБРАБОТЧИК КОНТАКТА ====================

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отправки контакта"""
    contact = update.message.contact
    user = update.effective_user

    phone = contact.phone_number if contact else "не указан"
    name = user.full_name
    username = user.username or "без username"
    user_id = user.id

    lead_info = (
        f"🆕 НОВАЯ ЗАЯВКА (КОНТАКТ)!\n\n"
        f"👤 Имя: {name}\n"
        f"📱 Телефон: {phone}\n"
        f"🆔 Username: @{username}\n"
        f"🆔 User ID: {user_id}\n"
        f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    logger.info(f"Контакт от {name} (@{username}): {phone}")

    admin_chat_id = os.getenv("ADMIN_CHAT_ID")
    if admin_chat_id:
        try:
            await context.bot.send_message(
                chat_id=admin_chat_id,
                text=lead_info
            )
        except Exception as e:
            logger.error(f"Не удалось отправить админу: {e}")

    await update.message.reply_text(
        "✅ Спасибо! Мы получили ваш контакт и свяжемся с вами в течение 15 минут.",
        reply_markup=get_main_keyboard()
    )


# ==================== ОСНОВНОЙ ОБРАБОТЧИК (КНОПКИ + ЗАЯВКА) ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Единый обработчик всех текстовых сообщений"""
    text = update.message.text
    user = update.effective_user

    # Проверяем, есть ли активный процесс заявки
    if context.user_data.get('order_step'):
        # Пользователь в процессе заполнения заявки
        step = context.user_data.get('order_step')

        if text == BTN_BACK_TO_MENU:
            context.user_data.clear()
            await update.message.reply_text("🔙 Заявка отменена.", reply_markup=get_main_keyboard())
            return

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
                f"👤 Имя: {context.user_data.get('name')}\n"
                f"📋 Проект: {context.user_data.get('project')}\n"
                f"💰 Бюджет: {context.user_data.get('budget')}\n"
                f"📞 Телефон: {context.user_data.get('phone')}\n"
                f"🆔 Username: @{user.username or 'нет'}\n"
                f"🆔 User ID: {user.id}\n"
                f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            logger.info(f"Заявка от {user.id}: {lead_info}")

            # Отправляем админу (если задан)
            admin_chat_id = os.getenv("ADMIN_CHAT_ID")
            if admin_chat_id:
                try:
                    await context.bot.send_message(
                        chat_id=admin_chat_id,
                        text=lead_info
                    )
                except Exception as e:
                    logger.error(f"Не удалось отправить админу: {e}")

            # ========== ОТПРАВКА НА Vertex_site_bot ==========
            global notifier_bot
            if not notifier_bot and NOTIFIER_TOKEN:
                from telegram.ext import ApplicationBuilder
                notifier_app = ApplicationBuilder().token(NOTIFIER_TOKEN).build()
                notifier_bot = notifier_app.bot
            
            if notifier_bot:
                try:
                    await notifier_bot.send_message(chat_id=YOUR_CHAT_ID, text=lead_info)
                    logger.info("Lead info sent to Vertex_site_bot")
                except Exception as e:
                    logger.error(f"Could not send to Vertex_site_bot: {e}")
            # ================================================

            await update.message.reply_text(
                TEXT_THANK_YOU,
                reply_markup=get_portfolio_inline_keyboard()
            )
            context.user_data.clear()

        return

    # Если нет активной заявки — обрабатываем кнопки меню
    if text == BTN_ABOUT:
        logger.info(f"Пользователь {user.id} запросил 'О нас'")
        await update.message.reply_text(TEXT_ABOUT, reply_markup=get_back_keyboard())

    elif text == BTN_SERVICES:
        logger.info(f"Пользователь {user.id} запросил 'Услуги'")
        await update.message.reply_text(TEXT_SERVICES, reply_markup=get_back_keyboard())

    elif text == BTN_PORTFOLIO:
        logger.info(f"Пользователь {user.id} запросил 'Портфолио'")
        await update.message.reply_text(
            "🖼 Наше портфолио\n\nНажмите на кнопку ниже:",
            reply_markup=get_portfolio_inline_keyboard()
        )

    elif text == BTN_CONTACTS:
        logger.info(f"Пользователь {user.id} запросил 'Контакты'")
        await update.message.reply_text(
            f"{TEXT_CONTACTS}\n\n"
            f"📧 Email: vertexsite07@gmail.com\n"
            f"📱 Telegram: https://t.me/Fulstak_raz",
            reply_markup=get_back_keyboard()
        )

    elif text == BTN_FAQ:
        logger.info(f"Пользователь {user.id} запросил 'FAQ'")
        await update.message.reply_text(TEXT_FAQ, reply_markup=get_back_keyboard())

    elif text == BTN_CALC:
        logger.info(f"Пользователь {user.id} открыл калькулятор цен")
        await update.message.reply_text(
            "🧮 КАЛЬКУЛЯТОР ЦЕН\n\nВыберите тип проекта:",
            reply_markup=get_calculator_keyboard()
        )

    elif text == BTN_ORDER:
        logger.info(f"Пользователь {user.id} начал оформление заявки")
        context.user_data['order_step'] = 'name'
        await update.message.reply_text(
            TEXT_ORDER_REQUEST,
            reply_markup=ReplyKeyboardMarkup([[BTN_BACK_TO_MENU]], resize_keyboard=True)
        )

    elif text == BTN_BACK_TO_MENU:
        context.user_data.clear()
        await update.message.reply_text(
            "🔙 Возвращаемся в главное меню:",
            reply_markup=get_main_keyboard()
        )

    else:
        await update.message.reply_text(
            "❓ Пожалуйста, выберите пункт из меню.",
            reply_markup=get_main_keyboard()
        )


# ==================== ОБРАБОТЧИК КАЛЬКУЛЯТОРА ====================

async def handle_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    prices = {
        "price_landing": "📄 Landing page\n💰 от 1500 ₽\n📅 2-4 дней",
        "price_corporate": "🏢 Корпоративный сайт\n💰 от 3500 ₽\n📅 3-6 дней",
        "price_shop": "🛒 Интернет-магазин\n💰 от 6000 ₽\n📅 14-21 день",
        "price_app": "📱 Мобильное приложение\n💰 от 8000 ₽\n📅 от 10 дней",
        "price_bot": "🤖 Telegram бот\n💰 от 1200 ₽\n📅 2-3 дней",
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
    await query.edit_message_text(
        "🧮 КАЛЬКУЛЯТОР ЦЕН\n\nВыберите тип проекта:",
        reply_markup=get_calculator_keyboard()
    )


# ==================== ОБРАБОТЧИК INLINE КНОПОК ====================

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data.startswith("price_"):
        await handle_calculator(update, context)
    elif query.data == "back_to_calc":
        await handle_back_to_calc(update, context)
    elif query.data == "order":
        await query.answer()
        await query.message.reply_text(
            "📝 Оставьте заявку через главное меню — кнопка 'Оставить заявку'"
        )
    else:
        await query.answer()


# ==================== ЗАПУСК БОТА ====================

def main():
    global notifier_bot
    
    # Инициализация второго бота (Vertex_site_bot)
    if NOTIFIER_TOKEN and not notifier_bot:
        from telegram.ext import ApplicationBuilder
        notifier_app = ApplicationBuilder().token(NOTIFIER_TOKEN).build()
        notifier_bot = notifier_app.bot
        logger.info("Notifier bot (Vertex_site_bot) initialized")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    logger.info("🤖 Бот VERTEX запущен!")
    application.run_polling()


if __name__ == "__main__":
    main()
