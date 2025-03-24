from django.core.management.base import BaseCommand
from bot.services.telebot_service import TeleBotHandlersService


class Command(BaseCommand):
    help = "Запуск бота с помощью telebot"

    def handle(self, *args, **kwargs):
        telebot_service = TeleBotHandlersService()
        telebot_service.execute()
