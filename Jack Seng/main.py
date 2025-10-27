import json
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

DATA_FILE = 'users_data.json'
USER_IDS_FILE = 'user_ids.json'


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_user_ids():
    if os.path.exists(USER_IDS_FILE):
        with open(USER_IDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'next_id': 0, 'users': {}}


def save_user_ids(user_ids):
    with open(USER_IDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_ids, f, ensure_ascii=False, indent=2)


def get_user_personal_id(user_id):
    user_ids = load_user_ids()
    if user_id not in user_ids['users']:
        user_ids['users'][user_id] = user_ids['next_id']
        user_ids['next_id'] += 1
        save_user_ids(user_ids)
    return user_ids['users'][user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {
            'username': update.effective_user.username,
            'first_name': update.effective_user.first_name,
            'last_name': update.effective_user.last_name,
            'training_completed': False,
            'has_choice': False,
            'passport_issued': False,
            'in_training': False
        }
        save_data(data)

    user_data = data.get(user_id, {})
    has_choice = user_data.get('has_choice', False)

    if has_choice:
        keyboard = [
            ['📊 паспорт', '🧳 работа']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            'Ты снова тут🙂? Рад тебя видеть👀, как дела🤔?',
            reply_markup=reply_markup
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
            "2. Начать работу🧳\n"
            "3. Бесплатный бонус 🎁\n"
            "4. Получение машины🚗</blockquote>\n\n"
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
            'has_choice': False,
            'passport_issued': False,
            'in_training': False
        }

    if text == '✔️пройти':
        data[user_id]['training_completed'] = True
        data[user_id]['has_choice'] = True
        data[user_id]['in_training'] = True
        save_data(data)

        keyboard = [
            ['📊 паспорт', '🧳 работа']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            'выберите свой паспорт',
            reply_markup=reply_markup
        )

    elif text == '❌отказаться':
        data[user_id]['training_completed'] = False
        data[user_id]['has_choice'] = True
        data[user_id]['in_training'] = False
        save_data(data)
        keyboard = [
            ['📊 паспорт', '🧳 работа']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            'Вы отказались от обучения. ❌',
            reply_markup=reply_markup
        )

    elif text == '📊 паспорт':
        user_info = data[user_id]

        if user_info.get('in_training', False):
            keyboard = [
                [InlineKeyboardButton("🖋 оформить", callback_data="training_passport")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                'выберите "оформить"',
                reply_markup=reply_markup
            )
        else:
            personal_id = get_user_personal_id(user_id)

            if user_info.get('passport_issued', False):
                passport_text = (
                    "<b>Ваш паспорт:</b>\n"
                    "<blockquote>1. Имя: {first_name}\n"
                    "2. ID: {personal_id}\n"
                    "3. Возраст: 18 лет\n"
                    "4. Кошелек: 0\n"
                    "5. Брак: нету\n"
                    "6. Работа: нету</blockquote>"
                ).format(
                    first_name=user_info['first_name'],
                    personal_id=personal_id
                )
            else:
                passport_text = (
                    "<b>Ваш паспорт:</b>\n"
                    "<blockquote>1. Имя: нету\n"
                    "2. ID: нету\n"
                    "3. Возраст: 18 лет\n"
                    "4. Кошелек: 0\n"
                    "5. Брак: нету\n"
                    "6. Работа: нету</blockquote>"
                )

            if not user_info.get('passport_issued', False):
                keyboard = [
                    [InlineKeyboardButton("🖋 оформление", callback_data="start_passport")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
            else:
                reply_markup = None

            await update.message.reply_text(
                passport_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

    elif text == '🧳 работа':
        if data[user_id].get('in_training', False):
            keyboard = [
                ['отменить❌', 'продолжить✅']
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_text(
                'вы проходите обучение, хотите отменить?',
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("📦грузчик", callback_data="work_loader")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                'доступные работы🧳',
                reply_markup=reply_markup
            )

    elif text == 'отменить❌':
        data[user_id]['in_training'] = False
        data[user_id]['training_completed'] = False
        save_data(data)

        keyboard = [
            ['📊 паспорт', '🧳 работа']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            'Обучение отменено',
            reply_markup=reply_markup
        )

    elif text == 'продолжить✅':
        keyboard = [
            ['📊 паспорт', '🧳 работа']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            'выберите свой паспорт',
            reply_markup=reply_markup
        )

    save_data(data)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    data = load_data()

    await query.answer()

    if query.data == "training_passport":
        await query.edit_message_text('начните оформление')

        emojis = ['🖋', '📄', '✅']
        random.shuffle(emojis)

        keyboard = [
            [InlineKeyboardButton(emojis[0], callback_data=f"training_step1_{emojis[0]}")],
            [InlineKeyboardButton(emojis[1], callback_data=f"training_step1_{emojis[1]}")],
            [InlineKeyboardButton(emojis[2], callback_data=f"training_step1_{emojis[2]}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            'оформление началось выберите 🖋',
            reply_markup=reply_markup
        )

    elif query.data.startswith("training_step1_"):
        selected_emoji = query.data.split('_')[2]

        if selected_emoji == '🖋':
            emojis = ['🖋', '📄', '✅']
            random.shuffle(emojis)

            keyboard = [
                [InlineKeyboardButton(emojis[0], callback_data=f"training_step2_{emojis[0]}")],
                [InlineKeyboardButton(emojis[1], callback_data=f"training_step2_{emojis[1]}")],
                [InlineKeyboardButton(emojis[2], callback_data=f"training_step2_{emojis[2]}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                'выберите 📄',
                reply_markup=reply_markup
            )

    elif query.data.startswith("training_step2_"):
        selected_emoji = query.data.split('_')[2]

        if selected_emoji == '📄':
            emojis = ['🖋', '📄', '✅']
            random.shuffle(emojis)

            keyboard = [
                [InlineKeyboardButton(emojis[0], callback_data=f"training_step3_{emojis[0]}")],
                [InlineKeyboardButton(emojis[1], callback_data=f"training_step3_{emojis[1]}")],
                [InlineKeyboardButton(emojis[2], callback_data=f"training_step3_{emojis[2]}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                'выберите ✅',
                reply_markup=reply_markup
            )

    elif query.data.startswith("training_step3_"):
        selected_emoji = query.data.split('_')[2]

        if selected_emoji == '✅':
            data[user_id]['passport_issued'] = True
            data[user_id]['in_training'] = False
            save_data(data)

            await query.edit_message_text(
                'поздровляю вы прошли обучение'
            )

    elif query.data == "start_passport":
        await query.edit_message_text('начните оформление')

        emojis = ['🖋', '📄', '✅']
        random.shuffle(emojis)

        keyboard = [
            [InlineKeyboardButton(emojis[0], callback_data=f"passport_step1_{emojis[0]}")],
            [InlineKeyboardButton(emojis[1], callback_data=f"passport_step1_{emojis[1]}")],
            [InlineKeyboardButton(emojis[2], callback_data=f"passport_step1_{emojis[2]}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(
            'оформление началось выберите 🖋',
            reply_markup=reply_markup
        )

    elif query.data.startswith("passport_step1_"):
        selected_emoji = query.data.split('_')[2]

        if selected_emoji == '🖋':
            emojis = ['🖋', '📄', '✅']
            random.shuffle(emojis)

            keyboard = [
                [InlineKeyboardButton(emojis[0], callback_data=f"passport_step2_{emojis[0]}")],
                [InlineKeyboardButton(emojis[1], callback_data=f"passport_step2_{emojis[1]}")],
                [InlineKeyboardButton(emojis[2], callback_data=f"passport_step2_{emojis[2]}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                'выберите 📄',
                reply_markup=reply_markup
            )

    elif query.data.startswith("passport_step2_"):
        selected_emoji = query.data.split('_')[2]

        if selected_emoji == '📄':
            emojis = ['🖋', '📄', '✅']
            random.shuffle(emojis)

            keyboard = [
                [InlineKeyboardButton(emojis[0], callback_data=f"passport_step3_{emojis[0]}")],
                [InlineKeyboardButton(emojis[1], callback_data=f"passport_step3_{emojis[1]}")],
                [InlineKeyboardButton(emojis[2], callback_data=f"passport_step3_{emojis[2]}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                'выберите ✅',
                reply_markup=reply_markup
            )

    elif query.data.startswith("passport_step3_"):
        selected_emoji = query.data.split('_')[2]

        if selected_emoji == '✅':
            data[user_id]['passport_issued'] = True
            save_data(data)

            personal_id = get_user_personal_id(user_id)
            user_info = data[user_id]

            passport_text = (
                "<b>Ваш паспорт:</b>\n"
                "<blockquote>1. Имя: {first_name}\n"
                "2. ID: {personal_id}\n"
                "3. Возраст: 18 лет\n"
                "4. Кошелек: 0\n"
                "5. Брак: нету\n"
                "6. Работа: нету</blockquote>"
            ).format(
                first_name=user_info['first_name'],
                personal_id=personal_id
            )

            await query.edit_message_text(
                f"поздровляю вы оформили паспорт\n\n{passport_text}",
                parse_mode='HTML'
            )

    elif query.data == "work_loader":
        keyboard = [
            [InlineKeyboardButton("назад", callback_data="back_to_work")],
            [InlineKeyboardButton("устроиться🧱", callback_data="get_job_loader")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(r"C:\Users\никита\Documents\Jack Seng\грузчик.jpg", 'rb') as photo:
            await query.message.reply_photo(
                photo=photo,
                caption=(
                    "💼 Работа [📦грузчик]🤝\n\n"
                    "Зарплата составляет за🤔 одну выгрузку 3000$🤝\n\n"
                    "Критерии:📊\n"
                    "18 лет🙂\n"
                    "Без опыта🤝\n\n"
                    "График работы 👀\n"
                    "1 — выгрузка = 1 минута 🤝\n\n"
                    "Ждем всех 💼"
                ),
                reply_markup=reply_markup
            )

    elif query.data == "back_to_work":
        keyboard = [
            [InlineKeyboardButton("📦грузчик", callback_data="work_loader")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            'доступные работы🧳',
            reply_markup=reply_markup
        )

    elif query.data == "get_job_loader":
        await query.edit_message_text('Вы устроились на работу 📦грузчик')


def main():
    print("Бот запущен")
    application = Application.builder().token("8202336530:AAGvVROUHMEV2Nqe6zvjtkSmt_-8AMbEdmQ").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling()


if __name__ == '__main__':
    main()