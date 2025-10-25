import json
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

DATA_FILE = 'users_data.json'


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {
            'username': update.effective_user.username,
            'first_name': update.effective_user.first_name,
            'last_name': update.effective_user.last_name,
            'training_completed': False,
            'has_choice': False
        }
        save_data(data)

    user_data = data.get(user_id, {})
    has_choice = user_data.get('has_choice', False)

    if has_choice:
        await update.message.reply_text(
            'Ты снова тут🙂? Рад тебя видеть👀, как дела🤔?',
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        keyboard = [
            ['✔️пройти', '❌отказаться']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        message_text = (
            "<code>🖐️ добро пожаловать✔️, хотите пройти обучение📌?</code>\n\n"
            "<b>Что будет в обучении:</b>\n"
            "<blockquote>1. Оформление паспорта📊\n"
            "2. Получение машины🚗\n"
            "3. Бесплатный бонус 🎁\n"
            "4. Получение одежды 👖\n"
            "5. Получение телефона 📱</blockquote>\n\n"
            "<b>Все то же самое будет и без обучения, но уже самостоятельно</b>"
        )

        await update.message.reply_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    data = load_data()

    if user_id not in data:
        data[user_id] = {
            'username': update.effective_user.username,
            'first_name': update.effective_user.first_name,
            'last_name': update.effective_user.last_name,
            'training_completed': False,
            'has_choice': False
        }

    if text == '✔️пройти':
        data[user_id]['training_completed'] = True
        data[user_id]['has_choice'] = True
        save_data(data)
        await update.message.reply_text(
            'Вы прошли обучение! ✅',
            reply_markup=ReplyKeyboardRemove()
        )

    elif text == '❌отказаться':
        data[user_id]['training_completed'] = False
        data[user_id]['has_choice'] = True
        save_data(data)
        await update.message.reply_text(
            'Вы отказались от обучения. ❌',
            reply_markup=ReplyKeyboardRemove()
        )

    save_data(data)


def main():
    application = Application.builder().token("8320402454:AAH-WGbDZr7Q8eD9RiI6WnWJkOtb_T-rJB0").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


if __name__ == '__main__':
    main()