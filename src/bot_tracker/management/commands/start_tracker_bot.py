from django.core.management.base import BaseCommand
from bot_tracker.main import bot_tracking


class Command(BaseCommand):
    help = "Запуск бота прослушки"

    def handle(self, *args, **kwargs):
        bot_tracking()
