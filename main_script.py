import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Bot
import openai
from apscheduler.schedulers.blocking import BlockingScheduler
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
    # код генерации контента
    # Пример:
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Напишите интересный пост об астрологии и таро.",
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Ошибка при генерации контента: {e}")
        return None

def generate_test_content():
    return "Тестовый пост"

# Функция публикации
def publish_post(context: CallbackContext):
    msg = generate_content()
    if msg:
        context.bot.send_message(chat_id=CHANNEL_NAME, text=msg)
    else:
        logging.info("Сообщение не было отправлено, так как контент пуст.")

# Планировщик
scheduler = BlockingScheduler(timezone=pytz.utc)
scheduler.add_job(publish_post, 'interval', seconds=5, args=[updater.job_queue])

# Тестирование
if __name__ == '__main__':
    updater.job_queue.run_repeating(publish_post, interval=5, first=0)

    updater.start_polling()
    updater.idle()

    # Запуск планировщика (если нужно)
    # scheduler.start()
