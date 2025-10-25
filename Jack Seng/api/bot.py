import json
import os
from http.server import BaseHTTPRequestHandler
import asyncio

# Импорты для Telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Для Vercel используем временную папку
DATA_FILE = '/tmp/users_data.json'


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Ваши обработчики
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


# Инициализация бота (только один раз)
def get_bot_application():
    token = os.getenv('BOT_TOKEN', '8320402454:AAH-WGbDZr7Q8eD9RiI6WnWJkOtb_T-rJB0')
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return application


# Глобальная переменная для хранения приложения
bot_application = get_bot_application()


# Обработчик для Vercel
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Telegram Bot is running on Vercel!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            # Обрабатываем обновление от Telegram
            update_dict = json.loads(post_data.decode('utf-8'))

            # Асинхронная обработка
            async def process_update():
                update = Update.de_json(update_dict, bot_application.bot)
                await bot_application.process_update(update)

            # Запускаем асинхронную задачу
            asyncio.run(process_update())

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "message": "Update processed"}
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(error_response).encode())