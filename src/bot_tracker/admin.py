from django.contrib import admin

from bot_tracker.models import TrackingChat


@admin.register(TrackingChat)
class TrackingChatAdmin(admin.ModelAdmin):
    list_display = ("title", "chat_id", "is_active")
    list_display_links = list_display
    search_fields = ("title", "chat_id")
    list_filter = ("is_active",)
