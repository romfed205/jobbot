from django.core.management.base import BaseCommand
from django_telethon.sessions import DjangoSession
from django_telethon.models import App, ClientSession
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient
from constance import config


class Command(BaseCommand):
    help = "Запуск бота прослушки"

    def handle(self, *args, **kwargs):
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
        else:
            print("Сессия уже авторизована")
