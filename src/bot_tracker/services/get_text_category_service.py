from bot.models import Category


class GetTextCategoryService:
    @classmethod
    def execute(cls, text):
        text = text.lower().strip()
        categories = Category.objects.filter(is_active=True)
        for category in categories:
            signal_words = category.signal_words.split("\n")
            for signal_word in signal_words:
                if signal_word.lower() in text:
                    return category
