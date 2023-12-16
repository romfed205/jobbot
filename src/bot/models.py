from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone
from dateutil.relativedelta import relativedelta


telegram_validator = [
    MinLengthValidator(
        limit_value=5,
        message='Ник должен быть не менее 5 символов'
    ),
    RegexValidator(
        regex="^[a-zA-Z0-9_]*$",
        message="Телеграм должен содержать только латиницу, цифры и символ '_'",
        code="invalid_telegram"
    )
]


class CustomUser(AbstractUser):
    telegram = models.CharField(
        "Телеграм",
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        validators=telegram_validator
    )
    chat_id = models.PositiveBigIntegerField("ID чата", null=True, blank=True, unique=True)
    categories = models.ManyToManyField(
        "bot.Category",
        related_name="users",
        through="bot.UserCategory",
        through_fields=("user", "category", "finish_date"),
        verbose_name="Категории",
        blank=True
    )
    objects = UserManager()

    class Meta:
        verbose_name = "пользователя"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.telegram} {self.chat_id}"

    def have_active_category(self, category):
        if not UserCategory.objects.filter(user=self, category=category).exists():
            return None, False

        user_category = UserCategory.objects.filter(user=self, category=category).first()
        return user_category, user_category.is_active

    def activate_subscription(self, subscription, category):
        delta = subscription.get_delta()
        if not UserCategory.objects.filter(user=self, category=category).exists():
            user_category = UserCategory(
                user=self,
                category=category,
                finish_date=timezone.now() + delta
            )
            user_category.save()
            return user_category

        user_category = UserCategory.objects.filter(user=self, category=category).first()
        if user_category.is_active:
            user_category.finish_date += delta
        else:
            user_category.finish_date = timezone.now() + delta
        user_category.save()
        return user_category


class UserCategory(models.Model):
    user = models.ForeignKey(
        "bot.CustomUser",
        on_delete=models.CASCADE,
        related_name="user_categories",
        verbose_name="Пользователь"
    )
    category = models.ForeignKey(
        "bot.Category",
        on_delete=models.CASCADE,
        related_name="user_categories",
        verbose_name="Категория"
    )
    finish_date = models.DateTimeField("Дата окончания подписки")

    class Meta:
        verbose_name = "категорию пользователя"
        verbose_name_plural = "Категории пользователей"

    @property
    def is_active(self):
        return self.finish_date >= timezone.now()


class Category(models.Model):
    title = models.CharField("Название", max_length=100)
    signal_words = models.TextField("Сигнальные слова", default="")
    subscriptions = models.ManyToManyField(
        "bot.Subscription",
        related_name="categories",
        verbose_name="Подписки",
        through="bot.CategorySubscription",
        through_fields=("category", "subscription"),
        blank=True
    )
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "категорию"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class CategorySubscription(models.Model):
    subscription = models.ForeignKey(
        "bot.Subscription",
        on_delete=models.CASCADE,
        related_name="category_subscriptions",
        verbose_name="Подписка"
    )
    category = models.ForeignKey(
        "bot.Category",
        on_delete=models.CASCADE,
        related_name="category_subscriptions",
        verbose_name="Категория"
    )

    class Meta:
        verbose_name = "подписку категории"
        verbose_name_plural = "Подписки категорий"


class Currency(models.Model):
    title = models.CharField("Название", max_length=100)
    currency_requisites = models.TextField("Реквизиты")
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "валюту"
        verbose_name_plural = "Валюты"

    def __str__(self):
        return self.title


class Subscription(models.Model):
    DAY_DURATION_TYPE = "day"
    WEEK_DURATION_TYPE = "week"
    MONTH_DURATION_TYPE = "month"
    DURATION_TYPES = (
        (DAY_DURATION_TYPE, "День"),
        (WEEK_DURATION_TYPE, "Неделя"),
        (MONTH_DURATION_TYPE, "Месяц")
    )

    title = models.CharField("Название", max_length=100)
    duration_type = models.CharField("Тип продолжительности", max_length=20, choices=DURATION_TYPES, default=DAY_DURATION_TYPE)
    duration_value = models.IntegerField("Продолжительность", default=1)
    prices = models.ManyToManyField(
        "bot.Currency",
        related_name="subscriptions",
        through="bot.SubscriptionPrice",
        through_fields=("subscription", "currency", "price"),
        verbose_name="Цены",
        blank=True
    )

    class Meta:
        verbose_name = "подписку"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return self.title

    def get_delta(self):
        if self.duration_type == "month":
            return relativedelta(months=self.duration_value)
        value = self.duration_value
        if self.duration_type == "week":
            value *= 7
        return relativedelta(days=value)


class SubscriptionPrice(models.Model):
    subscription = models.ForeignKey(
        "bot.Subscription",
        on_delete=models.CASCADE,
        related_name="subscription_prices",
        verbose_name="Подписка"
    )
    currency = models.ForeignKey(
        "bot.Currency",
        on_delete=models.CASCADE,
        related_name="subscription_prices",
        verbose_name="Валюта"
    )
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "цену подписки"
        verbose_name_plural = "Цены подписок"


class Message(models.Model):
    TYPE_TEXT = "text"
    TYPE_PHOTO = "photo"
    TYPE_VOICE = "voice"
    TYPE_DOCUMENT = "document"
    TYPE_VIDEO = "video"
    TYPES = (
        (TYPE_TEXT, "Текст"),
        (TYPE_PHOTO, "Фото"),
        (TYPE_VOICE, "Голосовое"),
        (TYPE_DOCUMENT, "Документ"),
        (TYPE_VIDEO, "Видео"),
    )

    PARSE_MODE_NO = "no"
    PARSE_MODE_YES = "yes"
    PARSE_MODE_CHOICES = (
        (PARSE_MODE_NO, "Нет"),
        (PARSE_MODE_YES, "Да")
    )

    name = models.CharField("Название", max_length=100)
    text = models.TextField("Текст", max_length=4096)
    loaded_file = models.FileField("Файл", upload_to="message_file/%Y-%m-%d-%H:%M:%S", blank=True, null=True)
    loaded_file_id = models.CharField("ID файла", max_length=150, null=True, blank=True)
    message_type = models.CharField("Тип сообщения", max_length=20, choices=TYPES, default=TYPE_TEXT)
    parse_mode = models.CharField("Форматированный", max_length=5, choices=PARSE_MODE_CHOICES, default=PARSE_MODE_NO)
    recipients = models.ManyToManyField(
        "bot.CustomUser",
        through="MessageStatus",
        through_fields=("message", "user", "status"),
        related_name="messages",
        verbose_name="Получатели",
        blank=True,
    )

    class Meta:
        verbose_name = "рассылку"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return self.name


class MessageStatus(models.Model):
    STATUS_NEW = "new"
    STATUS_SENT = "sent"
    STATUS_ERROR = "error"
    STATUSES = (
        (STATUS_NEW, "Ещё не отправлено"),
        (STATUS_SENT, "Отправлено"),
        (STATUS_ERROR, "Ошибка отправки"),
    )

    message = models.ForeignKey("bot.Message", verbose_name="Сообщение", on_delete=models.CASCADE)
    user = models.ForeignKey("bot.CustomUser", verbose_name="Пользователь", on_delete=models.CASCADE)
    status = models.CharField("Статус доставки сообщения", max_length=5, choices=STATUSES, default=STATUS_NEW)
    error = models.CharField("Текст ошибки", max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name = "статус рассылки"
        verbose_name_plural = "Статусы рассылок"
