from django.contrib.auth import get_user_model
from constance import config

from .bot_main import bot
from bot.models import Category, Subscription, SubscriptionPrice, Currency
from bot.services.telebot_service.keyboards import (
    main_menu_markup,
    choose_category_markup,
    buy_subscription_to_choose_category,
    help_markup,
    get_subscriptions_by_category_markup,
    get_subscription_prices_markup,
    get_payment_contact_markup,
    get_currencies_keyboard
)

User = get_user_model()


class TeleBotHandlersService:
    def _run_handlers(self):
        @bot.message_handler(
            content_types=["audio", "document", "photo", "video", "video_note", "voice"],
            func=lambda message: User.objects.filter(is_staff=True, chat_id=message.chat.id).exists()
        )
        def get_file_id(message):
            print(message.chat.id)
            has_file = None
            try:
                if message.document:
                    bot.send_message(message.chat.id,
                                     f"{message.document.file_name}\ntype: DOCUMENT\nfile_id: {message.document.file_id}",
                                     protect_content=False)
                    has_file = True
                if message.audio:
                    bot.send_message(message.chat.id,
                                     f"{message.audio.file_name}\ntype: AUDIO\nfile_id: {message.audio.file_id}",
                                     protect_content=False)
                    has_file = True
                if message.photo:
                    if isinstance(message.photo, list):
                        photo = message.photo[-1]
                    else:
                        photo = message.photo
                    bot.send_message(message.chat.id, f"type: PHOTO\nfile_id: {photo.file_id}", protect_content=False)
                    has_file = True
                if message.video:
                    bot.send_message(message.chat.id,
                                     f"{message.video.file_name}\ntype: VIDEO\nfile_id: {message.video.file_id}",
                                     protect_content=False)
                    has_file = True
                if not has_file:
                    bot.send_message(message.chat.id, "Файл не распознан")
            except Exception:
                bot.send_message(message.chat.id, "Файл не распознан")

        @bot.callback_query_handler(func=lambda call: call.data.startswith("choose_category#"))
        def choose_category(call):
            user = User.objects.get(chat_id=call.message.chat.id)
            category = Category.objects.get(id=int(call.data.split("#")[1]))
            user_category, have_active_category = user.have_active_category(category)
            if have_active_category:
                bot.send_message(
                    call.message.chat.id,
                    config.SUBSCRIPTION_BY_CATEGORY_TEXT.format(category.title, user_category.finish_date.strftime("%d.%m.%Y %H:%M:%S"))
                )
            else:
                bot.send_message(
                    call.message.chat.id,
                    config.BUY_SUBSCRIPTION_TO_CHOOSE_CATEGORY_TEXT,
                    reply_markup=buy_subscription_to_choose_category()
                )

        @bot.callback_query_handler(func=lambda call: call.data == "choose_category_for_subscribe")
        def choose_category_for_subscribe(call):
            try:
                bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
            except:
                pass

            bot.send_message(
                call.message.chat.id,
                config.CHOOSE_CATEGORY_FOR_SUBSCRIPTION_TEXT,
                reply_markup=choose_category_markup("choose_category_for_subscription")
            )

        @bot.callback_query_handler(func=lambda call: call.data.startswith("choose_category_for_subscription#"))
        def choose_category_for_subscription(call):
            category = Category.objects.get(id=int(call.data.split("#")[1]))

            try:
                bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
            except:
                pass

            bot.send_message(
                call.message.chat.id,
                config.CHOOSE_SUBSCRIPTION_BY_CATEGORY_TEXT,
                reply_markup=get_currencies_keyboard(category)
            )

        @bot.callback_query_handler(func=lambda call: call.data.startswith("choose_currency#"))
        def choose_currency(call):
            category = Category.objects.get(id=int(call.data.split("#")[1]))
            currency = Currency.objects.get(id=int(call.data.split("#")[2]))

            try:
                bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
            except:
                pass

            bot.send_message(
                call.message.chat.id,
                config.CHOOSE_SUBSCRIPTION_PRICES_TEXT,
                reply_markup=get_subscription_prices_markup(category, currency)
            )

        @bot.callback_query_handler(func=lambda call: call.data.startswith("choose_subscription_price#"))
        def choose_subscription_price(call):
            price = SubscriptionPrice.objects.get(id=int(call.data.split("#")[1]))

            try:
                bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
            except:
                pass

            bot.send_message(
                call.message.chat.id,
                config.PRICE_DESCRIPTION_TEXT.format(price.subscription.title, price.price, price.currency.title, price.currency.currency_requisites),
                reply_markup=get_payment_contact_markup()
            )

        @bot.message_handler(commands=["start"])
        def _add_user(message):
            if User.objects.filter(chat_id=message.chat.id).exists():
                bot.send_message(
                    message.chat.id,
                    config.WELCOME_BACK_TEXT,
                    reply_markup=main_menu_markup()
                )
            else:
                user = User(
                    username=str(message.chat.id),
                    email=f"{message.chat.id}@gmail.com",
                    telegram=message.chat.username,
                    chat_id=message.chat.id
                )
                user.save()
                bot.send_message(
                    message.chat.id,
                    config.START_TEXT,
                    reply_markup=main_menu_markup()
                )

        @bot.message_handler(content_types=["text"])
        def _buttons_handler(message):
            if message.text == config.CHOOSE_CATEGORY_BTN_TEXT:
                bot.send_message(
                    message.chat.id,
                    config.CHOOSE_CATEGORY_TEXT,
                    reply_markup=choose_category_markup()
                )
            elif message.text == config.GET_SUBSCRIPTION_BTN_TEXT:
                bot.send_message(
                    message.chat.id,
                    config.CHOOSE_CATEGORY_FOR_SUBSCRIPTION_TEXT,
                    reply_markup=choose_category_markup("choose_category_for_subscription")
                )
            elif message.text == config.ABOUT_BTN_TEXT:
                bot.send_message(
                    message.chat.id,
                    config.ABOUT_TEXT
                )
            elif message.text == config.HELP_BTN_TEXT:
                bot.send_message(
                    message.chat.id,
                    config.HELP_TEXT,
                    reply_markup=help_markup()
                )
            elif message.text == config.LINE_TO_SUPPORT_BTN_TEXT:
                bot.send_message(
                    message.chat.id,
                    config.LINE_TO_SUPPORT_TEXT
                )
            elif message.text == config.FAQ_BTN_TEXT:
                bot.send_message(
                    message.chat.id,
                    config.FAQ_TEXT
                )
            elif message.text == config.BACK_BTN_TEXT:
                bot.send_message(
                    message.chat.id,
                    config.MAIN_MENU_TEXT,
                    reply_markup=main_menu_markup()
                )

    def execute(self):
        self._run_handlers()
        bot.infinity_polling(timeout=100, long_polling_timeout=100)
