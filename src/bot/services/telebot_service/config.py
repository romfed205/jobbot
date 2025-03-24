from django.db import models


class MessageType(models.TextChoices):
    text = "text"
    audio = "audio"
    document = "document"
    photo = "photo"
    video = "video"
    voice = "voice"
