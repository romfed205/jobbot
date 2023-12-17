from django.utils import timezone
from bot.models import UserCategory
from bot.services.telebot_service.bot_main import bot
from bot.services.telebot_service.keyboards import get_vacancy_footer_keyboard


class SendVacancyToUsersByCategory:
    @classmethod
    def execute(cls, category, event):
        users_categories = UserCategory.objects.filter(
            category=category,
            finish_date__gte=timezone.now()
        ).select_related("user")
        keyboard = get_vacancy_footer_keyboard(event.message.sender.username)

        text = f"{event.message.text}\n\n------------------\nЗаказ найден через: {event.message.chat.title}\n@{event.message.sender.username}"
        for user_category in users_categories:
            try:
                bot.send_message(
                    user_category.user.chat_id,
                    text,
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Проблема с отправкой пользователю {user_category.user}")
