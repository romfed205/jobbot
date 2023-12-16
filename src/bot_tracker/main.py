from telethon import TelegramClient, events
from constance import config
from asgiref.sync import sync_to_async

from bot_tracker.models import TrackingChat


def bot_tracking():
    with TelegramClient(config.TRACKING_SESSION_NAME, int(config.TRACKING_API_ID), config.TRACKING_API_HASH, system_version="4.16.30-vxCUSTOM") as client:

        @client.on(events.NewMessage(incoming=True))
        def tracking_handler(event):
            # if event.message.chat_id in set(sync_to_async(TrackingChat.objects.filter(is_active=True).values_list("chat_id", flat=True)))():
            print(event.message.chat_id)
            print("MESSAGE: ", event.message.text)

        client.run_until_disconnected()
