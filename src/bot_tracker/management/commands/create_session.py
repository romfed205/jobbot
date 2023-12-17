from django.core.management.base import BaseCommand
from constance import config
from telethon.sync import TelegramClient
from telethon.sessions import StringSession


class Command(BaseCommand):
    help = "Запуск бота прослушки"

    def handle(self, *args, **kwargs):
        API_ID = config.TRACKING_API_ID
        API_HASH = config.TRACKING_API_HASH

        with TelegramClient(StringSession(), API_ID, API_HASH, system_version="4.16.30-vxCUSTOM") as client:
            print(client.session.save())
