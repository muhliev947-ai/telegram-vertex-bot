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

# Токен бота из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не задан! Используйте: export BOT_TOKEN='ваш_токен'")

# URL портфолио
PORTFOLIO_URL = "https://next-site-self-two.vercel.app"

# ==================== ТЕКСТЫ КНОПОК ====================

BTN_ABOUT = "📖 О нас"
BTN_SERVICES = "💰 Услуги и цены"
BTN_PORTFOLIO = "🖼 Портфолио"
BTN_CONTACTS = "📞 Контакты"
BTN_SEND_CONTACT = "📲 Отправить контакт"
BTN_BACK_TO_MENU = "🔙 В главное меню"
BTN_ORDER = "📝 Оставить заявку"

# ==================== ТЕКСТОВЫЕ БЛОКИ ====================

TEXT_ABOUT = (
    "🏢 **КОМПАНИЯ VERTEX**\n\n"
    "Мы — команда профессионалов, специализирующаяся на разработке "
    "цифровых продуктов под ключ.\n\n"
    "**Чем мы занимаемся:**\n"
    "• Разработка сайтов\n"
    "• Интернет-магазины\n"
    "• Мобильные приложения\n"
    "• SaaS платформы\n"
    "• UI/UX дизайн\n"
    "• Telegram боты\n\n"
    "💡 **Почему мы?**\n"
    "• Цены ниже рынка при высоком качестве\n"
    "• Соблюдение сроков\n"
    "• Техподдержка после сдачи проекта"
)

TEXT_SERVICES = (
    "💎 **НАШИ УСЛУГИ И ЦЕНЫ**\n\n"
    "• Landing page — от 15 000 ₽\n"
    "• Корпоративный сайт — от 35 000 ₽\n"
    "• Интернет-магазин — от 60 000 ₽\n"
    "• SaaS / Дашборд — от 90 000 ₽\n"
    "• Мобильное приложение — от 80 000 ₽\n"
    "• Telegram бот — от 12 000 ₽\n\n"
    "⚡️ **Акция:** Скидка 15% при заказе сайта + бота!\n\n"
    "📞 Для точного расчёта — свяжитесь с нами."
)

TEXT_CONTACTS = (
    "📞 **СВЯЖИТЕСЬ С НАМИ**\n\n"
    "✉️ Email: vertexsite07@gmail.com\n"
    "📱 Telegram: @vertex_support\n"
    "💬 WhatsApp: +7 (928) 092-2250\n\n"
    "🕐 Режим работы: 10:00 — 20:00 МСК\n\n"
    "Или нажмите кнопку ниже, чтобы оставить заявку — "
    "мы свяжемся с вами в течение 15 минут!"
)

TEXT_ORDER_REQUEST = (
    "📝 **ОСТАВИТЬ ЗАЯВКУ**\n\n"
    "Поделитесь вашим номером телефона, и мы свяжемся с вами "
    "в ближайшее время для обсуждения проекта.\n\n"
    "📲 Нажмите кнопку ниже, чтобы отправить контакт."
)

TEXT_THANK_YOU = (
    "✅ **Спасибо за заявку!**\n\n"
    "Мы получили ваш контакт и свяжемся с вами в течение 15 минут.\n\n"
    "А пока можете посмотреть наше портфолио на сайте 👇"
)

TEXT_START = (
    "👋 **Добро пожаловать в VERTEX!**\n\n"
    "Мы создаём сайты, приложения, ботов и дизайн.\n\n"
    "📌 **Что вы хотите узнать?**\n\n"
    "• О нас — кто мы и чем занимаемся\n"
    "• Услуги и цены — что мы предлагаем\n"
    "• Портфолио — наши работы\n"
    "• Контакты — как с нами связаться\n\n"
    "Выберите раздел в меню ниже 👇"
)

TEXT_HELP = (
    "ℹ️ **СПРАВКА ПО БОТУ** ℹ️\n\n"
    "Команды:\n"
    "/start — главное меню\n"
    "/help — эта справка\n\n"
    "Кнопки меню:\n"
    "📖 О нас — информация о компании\n"
    "💰 Услуги и цены — прайс-лист\n"
    "🖼 Портфолио — ссылка на наши работы\n"
    "📞 Контакты — способы связи\n\n"
    "📝 Оставить заявку — отправьте свой контакт, и мы перезвоним"
)

# ==================== ЛОГИРОВАНИЕ ====================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ==================== КЛАВИАТУРЫ ====================

def get_main_keyboard():
    """Главное меню (ReplyKeyboardMarkup)"""
    return ReplyKeyboardMarkup(
        [
            [BTN_ABOUT, BTN_SERVICES],
            [BTN_PORTFOLIO, BTN_CONTACTS],
            [BTN_ORDER],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите пункт меню..."
    )


def get_contact_keyboard():
    """Клавиатура с кнопкой отправки контакта"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_SEND_CONTACT, request_contact=True)],
            [BTN_BACK_TO_MENU],
        ],
        resize_keyboard=True,
    )


def get_back_keyboard():
    """Клавиатура с кнопкой возврата в меню"""
    return ReplyKeyboardMarkup(
        [[BTN_BACK_TO_MENU]],
        resize_keyboard=True,
    )


def get_portfolio_inline_keyboard():
    """Inline-клавиатура с ссылкой на портфолио"""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🌐 Перейти на сайт", url=PORTFOLIO_URL)],
            [InlineKeyboardButton("📞 Связаться с нами", callback_data="contact")],
        ]
    )


# ==================== ОБРАБОТЧИКИ КОМАНД ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    logger.info(f"Пользователь {user.id} (@{user.username}) запустил бота")
    await update.message.reply_text(
        TEXT_START,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        TEXT_HELP,
        reply_markup=get_back_keyboard(),
        parse_mode="Markdown"
    )


# ==================== ОБРАБОТЧИКИ КНОПОК ====================

async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки главного меню"""
    text = update.message.text
    user = update.effective_user

    if text == BTN_ABOUT:
        logger.info(f"Пользователь {user.id} запросил 'О нас'")
        await update.message.reply_text(
            TEXT_ABOUT,
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )

    elif text == BTN_SERVICES:
        logger.info(f"Пользователь {user.id} запросил 'Услуги и цены'")
        await update.message.reply_text(
            TEXT_SERVICES,
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )

    elif text == BTN_PORTFOLIO:
        logger.info(f"Пользователь {user.id} запросил 'Портфолио'")
        await update.message.reply_text(
            "🖼 **Наше портфолио**\n\nНажмите на кнопку ниже, чтобы посмотреть наши работы на сайте:",
            reply_markup=get_portfolio_inline_keyboard(),
            parse_mode="Markdown"
        )

    elif text == BTN_CONTACTS:
        logger.info(f"Пользователь {user.id} запросил 'Контакты'")
        await update.message.reply_text(
            TEXT_CONTACTS,
            reply_markup=get_back_keyboard(),
            parse_mode="Markdown"
        )

    elif text == BTN_ORDER:
        logger.info(f"Пользователь {user.id} хочет оставить заявку")
        await update.message.reply_text(
            TEXT_ORDER_REQUEST,
            reply_markup=get_contact_keyboard(),
            parse_mode="Markdown"
        )

    elif text == BTN_BACK_TO_MENU:
        await update.message.reply_text(
            "🔙 Возвращаемся в главное меню:",
            reply_markup=get_main_keyboard()
        )

    else:
        await update.message.reply_text(
            "❓ Пожалуйста, выберите пункт из меню.",
            reply_markup=get_main_keyboard()
        )


# ==================== ОБРАБОТЧИК КОНТАКТОВ ====================

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик получения контакта от пользователя"""
    contact = update.message.contact
    user = update.effective_user
    
    phone = contact.phone_number if contact else "не указан"
    name = user.full_name
    username = user.username or "без username"
    user_id = user.id
    
    # Формируем сообщение для лога (можно отправить себе в Telegram)
    lead_info = (
        f"🆕 **НОВАЯ ЗАЯВКА!**\n\n"
        f"👤 Имя: {name}\n"
        f"📱 Телефон: {phone}\n"
        f"🆔 Username: @{username}\n"
        f"🆔 User ID: {user_id}\n"
        f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    # Логируем в консоль
    logger.info(f"Заявка от {name} (@{username}): {phone}")
    
    # Отправляем уведомление админу (если указан ADMIN_CHAT_ID)
    admin_chat_id = os.getenv("ADMIN_CHAT_ID")
    if admin_chat_id:
        try:
            await context.bot.send_message(
                chat_id=admin_chat_id,
                text=lead_info,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу: {e}")
    
    # Благодарим пользователя
    await update.message.reply_text(
        TEXT_THANK_YOU,
        reply_markup=get_portfolio_inline_keyboard(),
        parse_mode="Markdown"
    )


# ==================== ОБРАБОТЧИК INLINE КНОПОК ====================

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на inline-кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "contact":
        await query.edit_message_text(
            TEXT_ORDER_REQUEST,
            reply_markup=get_contact_keyboard(),
            parse_mode="Markdown"
        )


# ==================== ЗАПУСК БОТА ====================

def main():
    """Главная функция запуска бота (без asyncio.run())"""
    application = Application.builder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    logger.info("🤖 Бот VERTEX запущен и готов к работе!")
    
    # Запуск бота (polling) - БЕЗ предварительного asyncio.run()
    application.run_polling()


if __name__ == "__main__":
    main()
