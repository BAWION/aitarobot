import telebot
import openai
from telebot import types
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')

openai.api_key = OPENAI_TOKEN

bot = telebot.TeleBot(TELEGRAM_TOKEN)

users = {}

def get_prediction(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот-предсказатель. Чтобы получить предсказание, зарегистрируйся командой /register")

@bot.message_handler(commands=['register'])  
def register(message):
    msg = bot.send_message(message.chat.id, "Как тебя зовут?")
    bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
    user_id = message.chat.id
    name = message.text
    users[user_id] = {'name': name}
    
    msg = bot.send_message(message.chat.id, "Какой у тебя знак Зодиака?")
    bot.register_next_step_handler(msg, process_zodiac_step, user_id)

def process_zodiac_step(message, user_id):
  zodiac = message.text
  users[user_id]['zodiac'] = zodiac
 
  msg = bot.send_message(message.chat.id, "Отправь фото своей ладони для предсказания")
  bot.register_next_step_handler(msg, process_photo_step, user_id)
  
def process_photo_step(message, user_id):
  photo_id = message.photo[-1].file_id
  users[user_id]['photo'] = photo_id  

  user = users[user_id]
  prompt = f"Provide astrology and tarot card prediction for {user['name']} with zodiac sign {user['zodiac']} based on palm photo: {user['photo']}"
  prediction = get_prediction(prompt)
  
  bot.send_message(message.chat.id, prediction)
  
bot.polling()