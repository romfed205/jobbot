from django.contrib.auth import get_user_model
from constance import config
from telebot.types import InputMediaPhoto

from .bot_main import bot
from bot.models import Category, Subscription, SubscriptionPrice, Currency
from bot.services.telebot_service.keyboards import *

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

        @bot.message_handler(commands=["start"])
        def add_user_handler(message):
            if User.objects.filter(chat_id=message.chat.id).exists():
                try:
                    bot.send_photo(
                        message.chat.id,
                        config.BOT_LOGO_IMAGE_ID,
                        caption=config.WELCOME_BACK_TEXT,
                        reply_markup=get_main_menu_inline_keyboard()
                    )
                except:
                    bot.send_message(
                        message.chat.id,
                        config.WELCOME_BACK_TEXT,
                        reply_markup=get_main_menu_inline_keyboard()
                    )
            else:
                user = User(
                    username=str(message.chat.id),
                    email=f"{message.chat.id}@gmail.com",
                    telegram=message.chat.username,
                    chat_id=message.chat.id
                )
                user.save()
                try:
                    bot.send_photo(
                        message.chat.id,
                        config.BOT_LOGO_IMAGE_ID,
                        caption=config.START_TEXT,
                        reply_markup=get_main_menu_inline_keyboard()
                    )
                except:
                    bot.send_message(
                        message.chat.id,
                        config.START_TEXT,
                        reply_markup=get_main_menu_inline_keyboard()
                    )

        @bot.callback_query_handler(func=lambda call: call.data == "main_menu")
        def main_menu_callback(call):
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=config.START_TEXT, reply_markup=get_main_menu_inline_keyboard())

        @bot.callback_query_handler(func=lambda call: call.data == "find_project")
        def find_project_callback(call):
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=config.CHOOSE_CATEGORY_TEXT, reply_markup=choose_category_markup())

        @bot.callback_query_handler(func=lambda call: call.data.startswith("choose_category#"))
        def choose_category_callback(call):
            _, category_id = call.data.split("#")
            category = Category.objects.get(id=int(category_id))
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=config.CHOOSE_CURRENCY_TEXT, reply_markup=get_currencies_keyboard(category))

        @bot.callback_query_handler(func=lambda call: call.data.startswith("choose_currency#"))
        def choose_currency_callback(call):
            _, category_id, currency_id = call.data.split("#")
            category = Category.objects.get(id=int(category_id))
            currency = Currency.objects.get(id=int(currency_id))
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=config.CHOOSE_SUBSCRIPTION_PRICES_TEXT, reply_markup=get_subscription_prices_markup(category, currency))

        @bot.callback_query_handler(func=lambda call: call.data.startswith("choose_subscription_price#"))
        def choose_price_callback(call):
            _, price_id = call.data.split("#")
            price = SubscriptionPrice.objects.get(id=int(price_id))
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=config.PRICE_DESCRIPTION_TEXT.format(price.subscription.title, price.price, price.currency.title, price.currency.currency_requisites), reply_markup=get_payment_contact_markup(price))

        @bot.callback_query_handler(func=lambda call: call.data == "about_callback")
        def about_callback(call):
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=config.ABOUT_TEXT, reply_markup=get_about_inline_keyboard())

        @bot.callback_query_handler(func=lambda call: call.data == "support_callback")
        def support_callback(call):
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=config.CONTACT_SUPPORT_TEXT.format(call.message.chat.id), reply_markup=contact_support_inline_keyboard())

        @bot.callback_query_handler(func=lambda call: call.data == "useful_callback")
        def useful_callback(call):
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=config.USEFUL_TEXT, reply_markup=useful_inline_keyboard())

    def execute(self):
        self._run_handlers()
        bot.infinity_polling(timeout=100, long_polling_timeout=100)
