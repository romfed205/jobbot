import os
from telethon.sync import TelegramClient
from django_telethon.sessions import DjangoSession
from django_telethon.models import App, ClientSession
from telethon.errors import SessionPasswordNeededError
from constance import config
from telethon import events

from bot_tracker.models import TrackingChat
from bot_tracker.services.get_text_category_service import GetTextCategoryService
from bot_tracker.services.send_vacancy_to_users_by_category import SendVacancyToUsersByCategory
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


def start_bot_tracker():
    API_ID = config.TRACKING_API_ID
    API_HASH = config.TRACKING_API_HASH

    app, is_created = App.objects.update_or_create(
        api_id=API_ID,
        api_hash=API_HASH
    )
    cs, cs_is_created = ClientSession.objects.update_or_create(
        name=config.TRACKING_SESSION_NAME,
    )
    telegram_client = TelegramClient(DjangoSession(client_session=cs), app.api_id, app.api_hash)
    telegram_client.connect()

    if not telegram_client.is_user_authorized():
        phone = input('Enter your phone number: ')
        telegram_client.send_code_request(phone)
        code = input('Enter the code you received: ')
        try:
            telegram_client.sign_in(phone, code)
        except SessionPasswordNeededError:
            password = input('Enter your password: ')
            telegram_client.sign_in(password=password)

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
