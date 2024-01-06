import os
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging

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

# Темы для генерации контента
topics = [
    "Влияние полнолуния на различные знаки зодиака",
    "История происхождения карт Таро",
    "Роль Меркурия в ретрограде в повседневной жизни",
    "Сравнение западной и восточной астрологии",
    "Как читать таро: основы для начинающих",
    "Символизм животных в астрологии",
    "Значение Солнца в астрологических домах",
    "Мифы и заблуждения о таро",
    "Планеты и их влияние на личность",
    "Использование астрологии для личностного роста",
    "Трактовка карты Рыцаря в Таро",
    "Секреты лунных фаз и их значение",
    "Астрология и ее связь с кармой",
    "Легенды и мифы о знаках зодиака",
    "Различные расклады карт Таро",
    "Как читать натальную карту",
    "Транзиты планет и их влияние на настроение",
    "Значение чисел в Таро",
    "Связь астрологии и медитации",
    "Анализ совместимости знаков зодиака",
    "Разбор каждой карты Таро: Арканы",
    "Астрологическое прогнозирование будущего",
    "Как использовать астрологию при принятии решений",
    "Как общаться с вашим духовным руководителем через Таро",
    "Сравнение различных школ Таро",
    "Планетарные переходы и их влияние на карьеру",
    "Символика и значение Луны в Таро",
    "Значение Солнечных и Лунных затмений",
    "Толкование обратных карт Таро",
    "Астрологическое значение Юпитера в вашем гороскопе"
]

current_topic_index = 0

# Функция генерации контента
def generate_content():
    global current_topic_index
    prompt_text = f"Напишите краткий, но полный абзац на тему '{topics[current_topic_index]}'. Закончите абзац полным предложением."
    full_text = ""
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt_text,
            max_tokens=250  # Увеличенное ограничение для каждого абзаца
        )
        paragraph = response.choices[0].text.strip()
        full_text += paragraph
        current_topic_index = (current_topic_index + 1) % len(topics)  # Переход к следующей теме
        return full_text
    except Exception as e:
        logging.error(f"Ошибка при генерации контента: {e}")
        return None

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
scheduler = BlockingScheduler(timezone=pytz.utc)
scheduler.add_job(
    publish_post_with_image, 
    CronTrigger(hour="9,15,21"),  # Запуск в 9:00, 15:00 и 21:00 по UTC
    args=[updater.job_queue]
)

# Регистрация обработчиков
updater.dispatcher.add_handler(CommandHandler("newpost", request_post))
updater.dispatcher.add_handler(MessageHandler(Filters.photo, photo_handler))

if __name__ == '__main__':
    updater.start_polling()
    updater.idle()

    # Запуск планировщика
    scheduler.start()
