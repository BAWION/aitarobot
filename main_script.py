import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot
import openai
from apscheduler.schedulers.blocking import BlockingScheduler

# Загрузка токенов API и имени канала из переменных среды
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')

# Проверка наличия всех необходимых данных
if not all([TELEGRAM_TOKEN, OPENAI_TOKEN, CHANNEL_NAME]):
    raise ValueError("Отсутствуют необходимые переменные среды: TELEGRAM_TOKEN, OPENAI_TOKEN, CHANNEL_NAME")

# Инициализация OpenAI
openai.api_key = OPENAI_TOKEN

# Инициализация бота Telegram
bot = Bot(TELEGRAM_TOKEN)

def generate_content():
    """
    Генерирует контент, используя модель GPT-3 от OpenAI.
    """
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Напишите интересный пост об астрологии и таро.",
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Ошибка при генерации контента: {e}")
        return None

def publish_post(context):
    """
    Публикует сгенерированный контент в Telegram канале.
    """
    content = generate_content()
    if content:
        try:
            context.bot.send_message(chat_id=CHANNEL_NAME, text=content)
        except Exception as e:
            print(f"Ошибка при публикации поста: {e}")
    else:
        print("Не удалось сгенерировать контент.")

# Создание экземпляра Updater
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

# Настройка планировщика для автоматической публикации постов
scheduler = BlockingScheduler()
scheduler.add_job(publish_post, 'cron', hour='9,15,21', args=(updater.job_queue,))  # Настройка на 9:00, 15:00 и 21:00

# Запуск планировщика
scheduler.start()
