from datetime import datetime, timedelta

from constance import config

from bot.models import Category, SentMessage, SpamCheck


class GetTextCategoryService:
    @classmethod
    def execute(cls, text):
        text = text.lower().strip()
        check_result = cls.check_text(text)
        if check_result is not True:
            return
        categories = Category.objects.filter(is_active=True)
        for category in categories:
            signal_words = category.signal_words.split("\n")
            for signal_word in signal_words:
                if signal_word.lower().strip() in text:
                    return category

    @classmethod
    def check_text(cls, text):
        if SpamCheck.objects.filter(text=text, is_active=True).exists():
            return
        if SentMessage.objects.filter(
                text=text,
                created_at__gte=datetime.now() - timedelta(hours=config.HOURS_TO_CHECK_DUPLICATES)
        ).exists():
            return
        return True
