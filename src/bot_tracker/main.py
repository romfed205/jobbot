import os
from telethon.sync import TelegramClient
from constance import config
from telethon import events
from telethon.sessions import StringSession

from bot_tracker.models import TrackingChat
from bot_tracker.services.get_text_category_service import GetTextCategoryService
from bot_tracker.services.send_vacancy_to_users_by_category import SendVacancyToUsersByCategory
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


def start_bot_tracker():
    API_ID = config.TRACKING_API_ID
    API_HASH = config.TRACKING_API_HASH
    STRING_SESSION = config.STRING_SESSION

    telegram_client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH, system_version="4.16.30-vxCUSTOM")
    telegram_client.connect()

    @telegram_client.on(events.NewMessage(incoming=True))
    async def tracking_handler(event):
        if event.message.chat_id in set(TrackingChat.objects.filter(is_active=True).values_list("chat_id", flat=True)):
            chat_title = event.message.chat.title
            sender_username = event.message.sender.username
            print("CHAT_TITLE: ", chat_title)
            print("SENDER_USERNAME: ", sender_username)
            category = GetTextCategoryService.execute(event.message.text)
            if category is not None:
                SendVacancyToUsersByCategory.execute(category, event)
            print(event.message.chat_id)
            print("MESSAGE: ", event.message.text)

    telegram_client.run_until_disconnected()
