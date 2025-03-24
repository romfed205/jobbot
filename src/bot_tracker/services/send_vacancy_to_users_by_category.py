from django.utils import timezone
from constance import config

from bot.models import UserCategory, SentMessage
from bot.services.telebot_service.bot_main import bot
from bot.services.telebot_service.keyboards import get_vacancy_footer_keyboard


class SendVacancyToUsersByCategory:
    @classmethod
    def execute(cls, category, event):
        users_categories = UserCategory.objects.filter(
            category=category,
            finish_date__gte=timezone.now()
        ).select_related("user")
        keyboard = get_vacancy_footer_keyboard(event)
        SentMessage.objects.create(category=category, text=event.message.text.lower().strip())
        text = f"{event.message.text}\n\n{config.BOT_INFO_FOOTER}"
        for user_category in users_categories:
            try:
                bot.send_message(
                    user_category.user.chat_id,
                    text,
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Проблема с отправкой пользователю {user_category.user}")
