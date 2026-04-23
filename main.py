from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from mcrcon import MCRcon
import re

# ===== НАСТРОЙКИ =====
TOKEN = "8780986312:AAHdW5dmnNpqSaJHLb4hYHX5b0FqtjBYphE"
ADMIN_ID = 8001700419
ADMIN_PASSWORD = "666123456k"
RCON_HOST = "65.21.70.50"
RCON_PORT = 25970
RCON_PASS = "MainworldsRCON2024"

# ===== RCON =====
def send_rcon(command: str) -> str:
    try:
        with MCRcon(RCON_HOST, RCON_PASS, port=RCON_PORT) as mcr:
            return mcr.command(command) or "✅ Выполнено"
    except Exception as e:
        return f"❌ Ошибка: {e}"

# ===== КНОПКИ ГЛАВНОГО МЕНЮ =====
def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("🐞 Сообщить о баге", callback_data="bug")],
        [InlineKeyboardButton("🚫 Сообщить о читере", callback_data="cheater")],
        [InlineKeyboardButton("📩 Написать админу", callback_data="report")],
        [InlineKeyboardButton("📢 Группа Telegram", callback_data="group")],
        [InlineKeyboardButton("🔧 Админ панель", callback_data="admin")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== АДМИН МЕНЮ =====
def admin_keyboard():
    keyboard = [
        [InlineKeyboardButton("💎 Выдать предмет", callback_data="give")],
        [InlineKeyboardButton("📢 Объявление", callback_data="broadcast")],
        [InlineKeyboardButton("📋 Консоль", callback_data="console")],
        [InlineKeyboardButton("🔙 Выйти", callback_data="back")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вас приветствует бот MainWorlds!\nЧем вам помочь?",
        reply_markup=main_keyboard()
    )

# ===== ОБРАБОТЧИК КНОПОК =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "group":
        await query.edit_message_text(
            "Наш Telegram-чат:\nhttps://t.me/mainworldF",
            reply_markup=main_keyboard()
        )

    elif data == "bug":
        context.user_data["report_type"] = "bug"
        context.user_data["waiting_report"] = True
        await query.edit_message_text("Опишите баг подробно.", reply_markup=main_keyboard())

    elif data == "cheater":
        context.user_data["report_type"] = "cheater"
        context.user_data["waiting_report"] = True
        await query.edit_message_text("Напишите ник читера и что он делает.", reply_markup=main_keyboard())

    elif data == "report":
        context.user_data["report_type"] = "question"
        context.user_data["waiting_report"] = True
        await query.edit_message_text("Напишите ваше сообщение. Администратор ответит.", reply_markup=main_keyboard())

    elif data == "admin":
        context.user_data["waiting_password"] = True
        await query.edit_message_text("Введите пароль для входа в админ-панель:")

    elif data == "back":
        context.user_data["admin_auth"] = False
        await query.edit_message_text("Вы вышли из админ-панели.", reply_markup=main_keyboard())

    elif data == "give":
        context.user_data["waiting_item"] = True
        await query.edit_message_text("Введите ник игрока:", reply_markup=admin_keyboard())

    elif data == "broadcast":
        context.user_data["waiting_broadcast"] = True
        await query.edit_message_text("Напишите текст объявления:", reply_markup=admin_keyboard())

    elif data == "console":
        context.user_data["waiting_console"] = True
        await query.edit_message_text("Введите консольную команду:", reply_markup=admin_keyboard())

# ===== ОБРАБОТКА ВСЕХ ТЕКСТОВЫХ СООБЩЕНИЙ =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    # Жалоба
    if context.user_data.get("waiting_report"):
        report_type = context.user_data.get("report_type", "unknown")
        if report_type == "bug":
            title = "🐞 БАГ"
        elif report_type == "cheater":
            title = "🚫 ЧИТЕР"
        else:
            title = "📩 ВОПРОС"
        
        await context.bot.send_message(
            ADMIN_ID,
            f"{title}\nОт: {user.first_name} (@{user.username})\nID: {user.id}\n\n{text}"
        )
        await update.message.reply_text("✅ Сообщение отправлено администратору!")
        context.user_data["waiting_report"] = False

    # Пароль для админ-панели
    elif context.user_data.get("waiting_password"):
        if text == ADMIN_PASSWORD:
            context.user_data["waiting_password"] = False
            context.user_data["admin_auth"] = True
            await update.message.reply_text("✅ Доступ разрешён!", reply_markup=admin_keyboard())
        else:
            context.user_data["waiting_password"] = False
            await update.message.reply_text("❌ Неверный пароль!", reply_markup=main_keyboard())

    # Выдать предмет (ввод ника)
    elif context.user_data.get("waiting_item"):
        context.user_data["nick"] = text
        context.user_data["waiting_item"] = False
        context.user_data["waiting_item_type"] = True
        await update.message.reply_text(
            "Что выдать?\n1. Алмаз 64\n2. Монетки 100\n3. Приват блок\n4. Талисман"
        )

    # Выдать предмет (выбор предмета)
    elif context.user_data.get("waiting_item_type"):
        nick = context.user_data.get("nick")
        choice = text
        if choice == "1":
            response = send_rcon(f"give {nick} diamond 64")
            await update.message.reply_text(f"✅ Выдано 64 алмаза игроку {nick}\n{response}")
        elif choice == "2":
            response = send_rcon(f"eco give {nick} 100")
            await update.message.reply_text(f"✅ Выдано 100 монеток игроку {nick}\n{response}")
        elif choice == "3":
            response = send_rcon(f"rg addmember {nick} home")
            await update.message.reply_text(f"✅ Игрок {nick} добавлен в приват\n{response}")
        elif choice == "4":
            response = send_rcon(f"mm i give {nick} LuckTotem 1")
            await update.message.reply_text(f"✅ Выдан талисман игроку {nick}\n{response}")
        else:
            await update.message.reply_text("❌ Неверный выбор")
        context.user_data["waiting_item_type"] = False

    # Объявление
    elif context.user_data.get("waiting_broadcast"):
        response = send_rcon(f"say §6📢 ОБЪЯВЛЕНИЕ: §f{text}")
        await update.message.reply_text(f"✅ Объявление отправлено!\n{response}")
        context.user_data["waiting_broadcast"] = False

    # Консоль
    elif context.user_data.get("waiting_console"):
        response = send_rcon(text)
        await update.message.reply_text(f"💻 Ответ:\n{response}")
        context.user_data["waiting_console"] = False

    else:
        await update.message.reply_text("❓ Используйте кнопки меню. /start")

# ===== ОТВЕТ АДМИНА ПОЛЬЗОВАТЕЛЮ =====
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID and update.message.reply_to_message:
        match = re.search(r"ID: (\d+)", update.message.reply_to_message.text)
        if match:
            user_id = int(match.group(1))
            await context.bot.send_message(
                user_id,
                f"📢 Ответ администратора:\n\n{update.message.text}"
            )
            await update.message.reply_text("✅ Ответ отправлен пользователю!")

# ===== ЗАПУСК =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.ALL, reply_to_user))
    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()