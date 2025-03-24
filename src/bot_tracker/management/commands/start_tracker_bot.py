from django.core.management.base import BaseCommand
from bot_tracker.main import start_bot_tracker


class Command(BaseCommand):
    help = "Запуск бота прослушки"

    def handle(self, *args, **kwargs):
        start_bot_tracker()
