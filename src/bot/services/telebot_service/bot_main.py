import telebot
from django.conf import settings

bot = telebot.TeleBot(settings.BOT_TOKEN, parse_mode=None)
