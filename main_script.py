import os
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging
import shutil

# Константы и инициализация
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
OPENAI_TOKEN = os.environ['OPENAI_TOKEN']
CHANNEL_NAME = os.environ['CHANNEL_NAME']

# Имя файла для временного хранения изображения
TEMP_IMAGE_PATH = 'temp_image.jpg'

openai.api_key = OPENAI_TOKEN
bot = Bot(TELEGRAM_TOKEN)
updater = Updater(TELEGRAM_TOKEN, use_context=True)

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Функции для генерации контента и обработка изображений
# ... (Код функции generate_content)

# Функция публикации поста с картинкой
def publish_post_with_image(context: CallbackContext):
    msg = generate_content()
    if msg:
        with open(TEMP_IMAGE_PATH, 'rb') as photo:
            context.bot.send_photo(chat_id=CHANNEL_NAME, photo=photo, caption=msg)
    else:
        logging.info("Сообщение не было отправлено, так как контент пуст.")

# Обработчик команды для запроса новой публикации
def request_post(update: Update, context: CallbackContext):
    if os.path.exists(TEMP_IMAGE_PATH):
        publish_post_with_image(context)
        os.remove(TEMP_IMAGE_PATH)  # Удалить временный файл изображения после публикации
        update.message.reply_text("Новый пост с картинкой был опубликован.")
    else:
        update.message.reply_text("Сначала загрузите картинку.")

# Обработчик для получения фотографий
def photo_handler(update: Update, context: CallbackContext):
    photo_file = update.message.photo[-1].get_file()
    photo_file.download(TEMP_IMAGE_PATH)
    update.message.reply_text("Картинка сохранена. Используйте /newpost для публикации.")

# Планировщик
# ... (Код планировщика)

# Регистрация обработчиков
updater.dispatcher.add_handler(CommandHandler("newpost", request_post))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))

if __name__ == '__main__':
    updater.start_polling()
    updater.idle()

    # Запуск планировщика
    scheduler.start()
