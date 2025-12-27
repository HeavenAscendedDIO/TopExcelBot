from telebot import TeleBot
from config import BOT_TOKEN
from handlers import start_handler

bot = TeleBot(BOT_TOKEN)

start_handler.register(bot)

bot.infinity_polling()