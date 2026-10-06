import os
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Этапы заполнения обращения
NICK, SERVER, CATEGORY, TEXT = range(4)

# Временное хранилище обращений
applications = {}

# -------------------------
# ГЛАВНОЕ МЕНЮ
# -------------------------

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("💡 Предложить идею", callback_data="idea"),
        ],
        [
            InlineKeyboardButton("🐞 Сообщить о проблеме", callback_data="problem"),
        ],
        [
            InlineKeyboardButton("📩 Обратиться к администрации", callback_data="admin"),
        ],
        [
            InlineKeyboardButton("ℹ️ Помощь", callback_data="help"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🦅 <b>OSPREY | ПРИЁМНАЯ</b>\n\n"
        "Добро пожаловать в официальную приёмную "
        "Заместителя Главного Администратора проекта "
        "<b>«Русь Мобайл»</b>.\n\n"
        "Здесь вы можете предложить идею, сообщить о проблеме "
        "или обратиться к администрации проекта.\n\n"
        "👇 Выберите необходимый раздел:"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


# -------------------------
# ОБРАБОТКА КНОПОК
# -------------------------

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "idea":
        context.user_data["type"] = "💡 Предложение идеи"

        await query.message.reply_text(
            "💡 <b>Предложение идеи</b>\n\n"
            "Давайте оформим ваше обращение.\n\n"
            "Введите ваш игровой никнейм:",
            parse_mode="HTML",
        )

        return NICK

    if query.data == "problem":
        context.user_data["type"] = "🐞 Сообщение о проблеме"

        await query.message.reply_text(
            "🐞 <b>Сообщение о проблеме</b>\n\n"
            "Введите ваш игровой никнейм:",
            parse_mode="HTML",
        )

        return NICK

    if query.data == "admin":
        context.user_data["type"] = "📩 Обращение к администрации"

        await query.message.reply_text(
            "📩 <b>Обращение к администрации</b>\n\n"
            "Введите ваш игровой никнейм:",
            parse_mode="HTML",
        )

        return NICK

    if query.data == "help":
        await query.message.reply_text(
            "ℹ️ <b>Помощь</b>\n\n"
            "Используйте главное меню, чтобы:\n\n"
            "💡 предложить идею;\n"
            "🐞 сообщить о проблеме;\n"
            "📩 обратиться к администрации.\n\n"
            "После заполнения обращения оно будет передано "
            "ответственному администратору.",
            parse_mode="HTML",
            reply_markup=main_menu(),
        )


# -------------------------
# ФОРМА ОБРАЩЕНИЯ
# -------------------------

async def get_nick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["nick"] = update.message.text

    await update.message.reply_text(
        "🎮 Теперь укажите сервер, на котором вы играете:"
    )

    return SERVER


async def get_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["server"] = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("🎮 Игровой процесс", callback_data="cat_game"),
        ],
        [
            InlineKeyboardButton("⚔️ Мероприятия", callback_data="cat_event"),
        ],
        [
            InlineKeyboardButton("🏢 Организации", callback_data="cat_org"),
        ],
        [
            InlineKeyboardButton("👑 Администрация", callback_data="cat_admin"),
        ],
        [
            InlineKeyboardButton("💡 Другое", callback_data="cat_other"),
        ],
    ]

    await update.message.reply_text(
        "📂 Выберите категорию обращения:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return CATEGORY


async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    categories = {
        "cat_game": "🎮 Игровой процесс",
        "cat_event": "⚔️ Мероприятия",
        "cat_org": "🏢 Организации",
        "cat_admin": "👑 Администрация",
        "cat_other": "💡 Другое",
    }

    context.user_data["category"] = categories.get(
        query.data,
        "💡 Другое",
    )

    await query.message.reply_text(
        "📝 Теперь подробно опишите ваше обращение.\n\n"
        "Постарайтесь максимально понятно изложить вашу мысль."
    )

    return TEXT


async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["text"] = update.message.text

    nick = context.user_data["nick"]
    server = context.user_data["server"]
    category = context.user_data["category"]
    request_type = context.user_data["type"]
    request_text = context.user_data["text"]

    preview = (
        "📋 <b>ПРОВЕРКА ОБРАЩЕНИЯ</b>\n\n"
        f"👤 Ник: <code>{nick}</code>\n"
        f"🎮 Сервер: <code>{server}</code>\n"
        f"📂 Категория: {category}\n"
        f"📌 Тип: {request_type}\n\n"
        f"📝 <b>Текст:</b>\n{request_text}\n\n"
        "Всё верно?"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Отправить",
                callback_data="submit",
            ),
            InlineKeyboardButton(
                "❌ Отменить",
                callback_data="cancel",
            ),
        ]
    ]

    await update.message.reply_text(
        preview,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return ConversationHandler.END


# -------------------------
# ОТПРАВКА / ОТМЕНА
# -------------------------

async def submit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        context.user_data.clear()

        await query.edit_message_text(
            "❌ Обращение отменено.\n\n"
            "Вы можете начать новое обращение через /start."
        )

        return

    # Пока заявка сохраняется локально.
    # На следующем этапе подключим Telegram ID администратора.
    applications[query.from_user.id] = {
        "nick": context.user_data.get("nick"),
        "server": context.user_data.get("server"),
        "category": context.user_data.get("category"),
        "type": context.user_data.get("type"),
        "text": context.user_data.get("text"),
    }

    await query.edit_message_text(
        "✅ <b>Обращение принято!</b>\n\n"
        "Спасибо за ваше обращение.\n"
        "Оно будет рассмотрено администрацией проекта.\n\n"
        "🦅 <b>Osprey | Приёмная</b>",
        parse_mode="HTML",
    )

    context.user_data.clear()


# -------------------------
# ОТМЕНА ДИАЛОГА
# -------------------------

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "❌ Заполнение обращения отменено.\n\n"
        "Чтобы начать заново, используйте /start."
    )

    return ConversationHandler.END


# -------------------------
# ЗАПУСК
# -------------------------

def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "Переменная BOT_TOKEN не настроена."
        )

    application = Application.builder().token(token).build()

    conversation_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                menu_callback,
                pattern="^(idea|problem|admin)$",
            )
        ],
        states={
            NICK: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_nick,
                )
            ],
            SERVER: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_server,
                )
            ],
            CATEGORY: [
                CallbackQueryHandler(
                    get_category,
                    pattern="^cat_",
                )
            ],
            TEXT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_text,
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel)
        ],
        allow_reentry=True,
    )

    application.add_handler(CommandHandler("start", start))

    application.add_handler(conversation_handler)

    application.add_handler(
        CallbackQueryHandler(
            submit_callback,
            pattern="^(submit|cancel)$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            menu_callback,
            pattern="^help$",
        )
    )

    print("🦅 Osprey | Приёмная запущена!")

    application.run_polling()


if __name__ == "__main__":
    main()
