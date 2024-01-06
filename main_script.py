import os
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
import logging

# Константы и инициализация
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
OPENAI_TOKEN = os.environ['OPENAI_TOKEN']
CHANNEL_NAME = os.environ['CHANNEL_NAME']

# Имя файла для временного хранения изображения
TEMP_IMAGE_PATH = 'temp_image.jpg'

# Глобальная переменная для хранения текущей темы
current_topic = None

openai.api_key = OPENAI_TOKEN
bot = Bot(TELEGRAM_TOKEN)
updater = Updater(TELEGRAM_TOKEN, use_context=True)

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Функция генерации контента по заданной теме
def generate_content(topic):
    prompt_text = f"Напишите краткий, но полный абзац на тему '{topic}'. Закончите абзац полным предложением."
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt_text,
            max_tokens=450
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Ошибка при генерации контента: {e}")
        return None

# Функция установки темы
def set_topic(update: Update, context: CallbackContext):
    global current_topic
    current_topic = ' '.join(context.args)
    if current_topic:
        update.message.reply_text(f"Тема установлена: {current_topic}")
    else:
        update.message.reply_text("Пожалуйста, укажите тему.")

# Функция публикации поста с картинкой и текстом
def publish_post_with_image_and_text(update: Update, context: CallbackContext):
    if current_topic and os.path.exists(TEMP_IMAGE_PATH):
        msg = generate_content(current_topic)
        with open(TEMP_IMAGE_PATH, 'rb') as photo:
            context.bot.send_photo(chat_id=CHANNEL_NAME, photo=photo, caption=msg)
        os.remove(TEMP_IMAGE_PATH)  # Удаление временного файла
        update.message.reply_text("Пост опубликован.")
    else:
        update.message.reply_text("Установите тему и загрузите картинку перед публикацией.")

# Обработчик для получения фотографий
def photo_handler(update: Update, context: CallbackContext):
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(TEMP_IMAGE_PATH)
    update.message.reply_text("Картинка сохранена.")

# Регистрация обработчиков
updater.dispatcher.add_handler(CommandHandler("settopic", set_topic, pass_args=True))
updater.dispatcher.add_handler(CommandHandler("publish", publish_post_with_image_and_text))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))

if __name__ == '__main__':
    updater.start_polling()
    updater.idle()
