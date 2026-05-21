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
# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = 1371388170 # ← Убедись, что это твой ID!
SITE_URL = "https://next-site-self-two.vercel.app"
PORTFOLIO_URL = "https://next-site-self-two.vercel.app/portfolio"
CONTACT_TELEGRAM = "@Fulstak_raz"
CONTACT_EMAIL = "vertexsite07@gmail.com"
CONTACT_PHONE = "+7 928 092-2250"
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found!")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
# =========================
# STATES
# =========================
NAME, PROJECT, BUDGET, CONTACT, CONFIRM = range(5)
# =========================
# KEYBOARDS
# =========================
MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["🏢 О студии", "💼 Услуги и цены"],
        ["🖼 Портфолио", "❓ FAQ"],
        ["📞 Контакты", "✍️ Оставить заявку"]
    ],
    resize_keyboard=True
)
CANCEL_MENU = ReplyKeyboardMarkup([["❌ Отменить"]], resize_keyboard=True)
# =========================
# TEXTS
# =========================
START_TEXT = "Здравствуйте!\n\nДобро пожаловать в **VERTEX** — студию премиального digital-разработки."
ABOUT_TEXT = (
    "🏢 **VERTEX** — цифровая студия полного цикла.\n\n"
    "Мы создаём современные сайты, дизайн и системы автоматизации, которые помогают бизнесу выделяться."
)
SERVICES_TEXT = (
    "💼 **Услуги и цены VERTEX**\n\n"
    "🖥 **Веб-разработка**\n"
    "• Landing page — от 1500 ₽\n"
    "• Корпоративный сайт — от 3500 ₽\n"
    "• Интернет-магазин — от 6000 ₽\n"
    "• SaaS / Дашборд — от 9000 ₽\n\n"
    "🎨 **Дизайн и брендинг**\n"
    "• Логотип и фирменный стиль — от 1000 ₽\n"
    "• UI/UX дизайн сайта — от 2000 ₽\n\n"
    "📈 **Продвижение**\n"
    "• SEO-оптимизация — от 1500 ₽\n"
    "• Контекстная реклама — от 2000 ₽\n\n"
    "🤖 **Автоматизация**\n"
    "• Telegram бот — от 1200 ₽\n"
    "• Интеграция с CRM — от 2500 ₽\n\n"
    "⚡️ **Акция:** Скидка 10% на первый проект!\n\n"
    f"🌐 Подробнее: [{SITE_URL}]({SITE_URL})"
)
PORTFOLIO_TEXT = (
    "🖼 **Наше портфолио**\n\n"
    "Примеры наших работ:\n\n"
    "🔹 Разработка сайтов под ключ\n"
    "🔹 Интернет-магазины\n"
    "🔹 Мобильные приложения\n"
    "🔹 Telegram боты\n"
    "🔹 UI/UX дизайн\n\n"
    f"👉 **Смотреть все работы:** [{PORTFOLIO_URL}]({PORTFOLIO_URL})"
)
FAQ_TEXT = (
    "❓ **Часто задаваемые вопросы**\n\n"
    "**• Сколько стоит сайт?**\n Цена зависит от сложности — от 1500 ₽.\n\n"
    "**• Сколько времени занимает разработка?**\n От 3 до 21 дня.\n\n"
    "**• Можно ли оплатить частями?**\n Да, поэтапно (предоплата 30-50%).\n\n"
    "**• Даёте ли гарантию?**\n Да, 30 дней бесплатной поддержки.\n\n"
    "**• Как начать?**\n Нажмите «Оставить заявку»."
)
CONTACTS_TEXT = (
    "📞 **Контакты VERTEX**\n\n"
    f"📱 Telegram: {CONTACT_TELEGRAM}\n"
    f"📧 Email: {CONTACT_EMAIL}\n"
    f"📞 Телефон: {CONTACT_PHONE}\n"
    f"🌐 Сайт: [{SITE_URL}]({SITE_URL})\n"
    f"🖼 Портфолио: [{PORTFOLIO_URL}]({PORTFOLIO_URL})\n\n"
    "🕒 Режим работы: 10:00 — 20:00 МСК"
)
# =========================
# SEND LEAD
# =========================
async def send_lead_to_admin(context, user_data, user):
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
   
    msg = (
        f"🔥 <b>НОВАЯ ЗАЯВКА VERTEX</b>\n\n"
        f"👤 Имя: {user_data['name']}\n"
        f"📋 Проект: {user_data['project']}\n"
        f"💰 Бюджет: {user_data['budget']}\n"
        f"📞 Контакт: {user_data['contact']}\n"
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
# HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(START_TEXT, reply_markup=MAIN_MENU, parse_mode='HTML')
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text in ["🏢 О студии", "О студии"]:
        await update.message.reply_text(ABOUT_TEXT, parse_mode='HTML')
    elif text in ["💼 Услуги и цены", "Услуги и цены"]:
        await update.message.reply_text(SERVICES_TEXT, parse_mode='HTML', disable_web_page_preview=True)
    elif text in ["🖼 Портфолио", "Портфолио"]:
        await update.message.reply_text(PORTFOLIO_TEXT, parse_mode='HTML', disable_web_page_preview=True)
    elif text in ["❓ FAQ", "FAQ"]:
        await update.message.reply_text(FAQ_TEXT, parse_mode='HTML')
    elif text in ["📞 Контакты", "Контакты"]:
        await update.message.reply_text(CONTACTS_TEXT, parse_mode='HTML', disable_web_page_preview=True)
    elif text == "✍️ Оставить заявку":
        await update.message.reply_text(
            "<b>Шаг 1 из 4</b>\nВведите ваше имя:",
            reply_markup=CANCEL_MENU,
            parse_mode='HTML'
        )
        return NAME
# Conversation (оставил без изменений, только улучшил confirm)
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
    preview = f"<b>Проверьте данные:</b>\n\n👤 {context.user_data['name']}\n📋 {context.user_data['project']}\n💰 {context.user_data['budget']}\n📞 {context.user_data['contact']}\n\nВсё верно?"
   
    confirm_keyboard = ReplyKeyboardMarkup([["✅ Да, отправить"], ["❌ Отменить"]], resize_keyboard=True)
    await update.message.reply_text(preview, reply_markup=confirm_keyboard, parse_mode='HTML')
    return CONFIRM
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    if any(word in text for word in ["да", "yes", "ок", "✅", "отправить"]):
        await send_lead_to_admin(context, context.user_data, update.effective_user)
        await update.message.reply_text("✅ <b>Заявка отправлена!</b>\nМы свяжемся с вами в ближайшее время.", reply_markup=MAIN_MENU, parse_mode='HTML')
    else:
        await update.message.reply_text("❌ Заявка отменена.", reply_markup=MAIN_MENU)
    context.user_data.clear()
    return ConversationHandler.END
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Заявка отменена.", reply_markup=MAIN_MENU)
    context.user_data.clear()
    return ConversationHandler.END
# =========================
# MAIN
# =========================
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
    print("✅ VERTEX Bot запущен!")
    app.run_polling()
if __name__ == "__main__":
    main()
