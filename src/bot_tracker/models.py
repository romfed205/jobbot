from django.db import models


class TrackingChat(models.Model):
    title = models.CharField("Название", max_length=200)
    chat_id = models.BigIntegerField("ID чата канала или чата")
    chat_source = models.CharField("Окончание ссылки на чат", max_length=200, null=True, blank=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "чат прослушки"
        verbose_name_plural = "Чаты прослушки"

    def __str__(self):
        return f"{self.title} ({self.chat_id})"
