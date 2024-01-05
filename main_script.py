
import os
import telebot
import openai
from apscheduler.schedulers.blocking import BlockingScheduler

# Загрузка токенов API и имени канала из переменных среды
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
CHANNEL_NAME = os.getenv('CHANNEL_NAME')

# Проверка наличия всех необходимых данных
if not all([TELEGRAM_TOKEN, OPENAI_TOKEN, CHANNEL_NAME]):
    raise ValueError("Отсутствуют необходимые переменные среды: TELEGRAM_TOKEN, OPENAI_TOKEN, CHANNEL_NAME")

# Инициализация бота и OpenAI
bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_TOKEN

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

def publish_post():
    """
    Публикует сгенерированный контент в Telegram канале.
    """
    content = generate_content()
    if content:
        try:
            bot.send_message(CHANNEL_NAME, content)
        except Exception as e:
            print(f"Ошибка при публикации поста: {e}")
    else:
        print("Не удалось сгенерировать контент.")

# Настройка планировщика для автоматической публикации постов
scheduler = BlockingScheduler()
scheduler.add_job(publish_post, 'cron', hour='9,15,21')  # Настройка на 9:00, 15:00 и 21:00

# Запуск планировщика
scheduler.start()
