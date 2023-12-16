from bot.services.telebot_service.bot_main import bot
from bot.services.telebot_service.config import MessageType


def send_tg_message(text, chat_id, message_type, file, file_id="", parse_mode={}):
    if file_id:
        file = file_id

    caption = {}
    if text:
        caption = {"caption": text}

    if message_type == MessageType.text:
        bot.send_message(chat_id, text, **parse_mode)

    if message_type == MessageType.photo:
        bot.send_photo(chat_id, file, **caption, **parse_mode)

    elif message_type == MessageType.voice:
        bot.send_document(chat_id, file, **caption, **parse_mode)

    elif message_type == MessageType.document:
        bot.send_document(chat_id, file, **caption, **parse_mode)

    elif message_type == MessageType.video:
        bot.send_video(chat_id, file, **caption, **parse_mode)
