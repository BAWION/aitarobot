import os
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import openai
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging

# Константы и инициализация
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
OPENAI_TOKEN = os.environ['OPENAI_TOKEN']
CHANNEL_NAME = os.environ['CHANNEL_NAME']

openai.api_key = OPENAI_TOKEN
bot = Bot(TELEGRAM_TOKEN)
updater = Updater(TELEGRAM_TOKEN, use_context=True)

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Функции для генерации контента
def generate_content():
    """
    Генерирует контент, используя модель GPT-3 от OpenAI.
    """
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Напишите интересный пост об астрологии и таро.",
            max_tokens=300  # Увеличено количество токенов
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Ошибка при генерации контента: {e}")
        return None

# Функция публикации
def publish_post(context: CallbackContext):
    msg = generate_content()
    if msg:
        context.bot.send_message(chat_id=CHANNEL_NAME, text=msg)
    else:
        logging.info("Сообщение не было отправлено, так как контент пуст.")

# Обработчик команды для запроса новой публикации
def request_post(update: Update, context: CallbackContext):
    publish_post(context)
    update.message.reply_text("Новый пост был опубликован.")

# Планировщик
scheduler = BlockingScheduler(timezone=pytz.utc)
scheduler.add_job(
    publish_post, 
    CronTrigger(hour="9,15,21"),  # Запуск в 9:00, 15:00 и 21:00 по UTC
    args=[updater.job_queue]
)

# Регистрация обработчиков
updater.dispatcher.add_handler(CommandHandler("newpost", request_post))

if __name__ == '__main__':
    updater.start_polling()
    updater.idle()

    # Запуск планировщика
    scheduler.start()
