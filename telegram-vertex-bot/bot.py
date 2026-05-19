import logging
import os
import asyncio

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
    ContextTypes,
    filters,
)

# Токен берём из переменной окружения Render
TOKEN = os.getenv("BOT_TOKEN")

# --- Тексты кнопок ---
BTN_ABOUT = "📖 О нас"
BTN_SERVICES = "💰 Услуги и цены"
BTN_PORTFOLIO = "🖼 Портфолио"
BTN_CONTACTS = "📞 Контакты / Оставить заявку"
BTN_SEND_CONTACT = "📲 Отправить контакт"

PORTFOLIO_URL = "https://next-site-self-two.vercel.app/portfolio"

# --- Текстовые блоки ---
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
    "💡 Цены ниже рынка при высоком качестве."
)

TEXT_SERVICES = (
    "💎 НАШИ УСЛУГИ И ЦЕНЫ\n\n"
    "• Landing page — от 15 000 ₽\n"
    "• Корпоративный сайт — от 35 000 ₽\n"
    "• Интернет-магазин — от 60 000 ₽\n"
    "• SaaS / Дашборд — от 90 000 ₽\n"
    "• Мобильное приложение — от 80 000 ₽\n"
    "• Telegram бот — от 12 000 ₽\n\n"
    "⚡️ Скидка 15% при заказе сайта + бота"
)

TEXT_CONTACTS = (
    "📞 СВЯЖИТЕСЬ С НАМИ\n\n"
    "✉️ Email: info@vertex.ru\n"
    "📱 Telegram: @vertex_support\n"
    "💬 WhatsApp: +7 (999) 123-45-67\n\n"
    "Или оставьте заявку — мы свяжемся с вами в течение 15 минут!"
)

TEXT_START = (
    "👋 Добро пожаловать в VERTEX!\n\n"
    "Мы создаём сайты, приложения, ботов и дизайн.\n\n"
    "Выберите раздел в меню ниже 👇"
)

TEXT_HELP = (
    "ℹ️ Справка по боту VERTEX\n\n"
    "/start — главное меню\n"
    "/help — помощь\n"
)

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_main_keyboard():
    return ReplyKeyboardMarkup(
        [
            [BTN_ABOUT, BTN_SERVICES],
            [BTN_PORTFOLIO],
            [BTN_CONTACTS],
        ],
        resize_keyboard=True
    )


def get_contacts_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_SEND_CONTACT, request_contact=True)],
            [BTN_ABOUT, BTN_SERVICES],
            [BTN_PORTFOLIO, BTN_CONTACTS],
        ],
        resize_keyboard=True
    )


def get_portfolio_inline_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Перейти в портфолио", url=PORTFOLIO_URL)]]
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXT_START, reply_markup=get_main_keyboard())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXT_HELP, reply_markup=get_main_keyboard())


async def handle_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == BTN_ABOUT:
        await update.message.reply_text(TEXT_ABOUT, reply_markup=get_main_keyboard())

    elif text == BTN_SERVICES:
        await update.message.reply_text(TEXT_SERVICES, reply_markup=get_main_keyboard())

    elif text == BTN_PORTFOLIO:
        await update.message.reply_text(
            "🖼 Наше портфолио:",
            reply_markup=get_portfolio_inline_keyboard(),
        )

    elif text == BTN_CONTACTS:
        await update.message.reply_text(TEXT_CONTACTS, reply_markup=get_contacts_keyboard())

    else:
        await update.message.reply_text(
            "Пожалуйста, выберите пункт из меню.",
            reply_markup=get_main_keyboard(),
        )


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone = contact.phone_number if contact else "не указан"

    user = update.effective_user
    logger.info("Заявка: user_id=%s, username=%s, phone=%s", user.id, user.username, phone)

    await update.message.reply_text(
        "✅ Спасибо! Мы свяжемся с вами в течение 15 минут.",
        reply_markup=get_main_keyboard(),
    )


async def run_bot():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_button))

    logger.info("Бот VERTEX запущен...")

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()


if __name__ == "__main__":
    asyncio.run(run_bot())
