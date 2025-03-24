from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django_admin_inline_paginator.admin import TabularInlinePaginated
from constance import config

from bot.models import (
    CustomUser,
    UserCategory,
    Category,
    Currency,
    Subscription,
    SubscriptionPrice,
    CategorySubscription,
    Message,
    MessageStatus,
    SpamCheck,
    SentMessage
)
from bot.services.telebot_service.bot_main import bot
from bot.services.telebot_service.mass_send import mass_send
from bot.forms import ActivateSubscriptionForm, MassMessageForm, StatusMessageForm, MessageForm


@admin.action(description="Отправить сообщение")
def send_message(modeladmin, request, users):
    form = None

    if "apply" in request.POST:
        form = MassMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=True)
            count, errors = mass_send(
                message,
                users
            )
            modeladmin.message_user(request, "Сообщение %s отправлено %d пользователям. %d ошибок отправки" % (message.name, count, errors))
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = MassMessageForm(initial={"_selected_action": request.POST.getlist(ACTION_CHECKBOX_NAME)})

    return render(request, "admin/users/mass_send.html", {"items": users, "form": form, "title": "Массовая отправка сообщения"})


@admin.action(description="Активировать подписку")
def activate_subscription(modeladmin, request, users):
    form = None

    if "apply" in request.POST:
        form = ActivateSubscriptionForm(request.POST, request.FILES)
        if form.is_valid():
            subscription = form.cleaned_data.get("subscription")
            category = form.cleaned_data.get("category")
            errors = 0
            success = 0
            for user in users:
                try:
                    user_category = user.activate_subscription(subscription, category)
                    bot.send_message(
                        user.chat_id,
                        config.ACTIVATE_SUBSCRIPTION_TEXT.format(
                            category.title,
                            user_category.finish_date.strftime("%d.%m.%Y %H:%M:%S")
                        )
                    )
                    success += 1
                except:
                    errors += 1

            modeladmin.message_user(request, "Подписка активирована %d пользователям." % (success))
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = ActivateSubscriptionForm(initial={'_selected_action': request.POST.getlist(ACTION_CHECKBOX_NAME)})

    return render(request, 'admin/users/activate_subscription.html', {'items': users, 'form': form, 'title': "Активация подписки"})


class UserCategoryInline(admin.StackedInline):
    model = UserCategory
    extra = 1
    can_delete = True


class SubscriptionPriceInline(admin.StackedInline):
    model = SubscriptionPrice
    extra = 1
    can_delete = True


class CategorySubscriptionInline(admin.StackedInline):
    model = CategorySubscription
    extra = 1
    can_delete = True


class StatusesInline(TabularInlinePaginated):
    form = StatusMessageForm
    model = MessageStatus
    per_page = 10
    extra = 1


class UserMessagesInline(TabularInlinePaginated):
    model = MessageStatus
    per_page = 5
    extra = 1
    can_delete = True


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("telegram", "chat_id")
    list_display_links = list_display
    search_fields = ("telegram", "chat_id")
    fieldsets = (
        ("Разрешения", {
            "fields": ("is_active", "is_staff", "is_superuser"),
        }),
        ("Информация", {"fields": ("telegram", "chat_id")}),
    )
    inlines = [UserCategoryInline, UserMessagesInline]
    actions = [activate_subscription, send_message]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active")
    list_display_links = list_display
    search_fields = ("title",)
    list_filter = ("is_active",)
    inlines = [CategorySubscriptionInline]


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "currency_requisites")
    list_display_links = list_display
    search_fields = ("title",)
    list_filter = ("is_active",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("title", "duration_type", "duration_value")
    list_display_links = list_display
    search_fields = ("title",)
    list_filter = ("duration_type",)
    inlines = [SubscriptionPriceInline, CategorySubscriptionInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    form = MessageForm
    list_display = ("name", "text")
    search_fields = ("name", "text")
    actions = ["send"]
    inlines = [StatusesInline]
    change_form_template = "admin/message/send.html"

    def send(self, request, queryset):
        users = []
        for message in queryset:
            statuses = MessageStatus.objects.filter(message=message)
            for status in statuses:
                if status.status != MessageStatus.STATUS_SENT:
                    users.append(status.user)
            count, errors = mass_send(message, users)
            self.message_user(request, "Сообщение %s отправлено %d пользователям. %d ошибок отправки" % (message.name, count, errors))

    send.short_description = "Отправить"


@admin.register(SentMessage)
class SentMessageAdmin(admin.ModelAdmin):
    list_display = ("category", "created_at")
    list_display_links = list_display
    search_fields = ("text",)
    list_filter = ("category",)


@admin.register(SpamCheck)
class SpamCheckAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active")
    list_display_links = list_display
    search_fields = ("title", "text")
    list_filter = ("is_active",)


admin.site.unregister(Group)
