import telebot
from constance import config

from bot.models import Category, Currency, Subscription, SubscriptionPrice, CategorySubscription
from bot_tracker.models import TrackingChat


def get_vacancy_footer_keyboard(event):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    author_username = event.message.sender.username
    if author_username:
        author_btn = telebot.types.InlineKeyboardButton(config.VACANCY_AUTHOR_BTN_INLINE, url=f"https://t.me/{author_username}")
        markup.add(author_btn)
    else:
        chat = TrackingChat.objects.filter(chat_id=event.message.chat_id).first()
        if chat and chat.chat_source:
            author_btn = telebot.types.InlineKeyboardButton(config.VACANCY_AUTHOR_BTN_INLINE, url=f"https://t.me/{chat.chat_source}/{event.message.id}")
            markup.add(author_btn)
    complaint_on_author_btn = telebot.types.InlineKeyboardButton(config.COMPLAINT_ON_AUTHOR_BTN_INLINE, url=f"https://t.me/{config.COMPLAINT_ACCOUNT_USERNAME}")
    markup.add(complaint_on_author_btn)
    return markup


def get_main_menu_inline_keyboard():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    find_project_btn = telebot.types.InlineKeyboardButton(config.FIND_PROJECT_BTN_INLINE, callback_data="find_project")
    about_btn = telebot.types.InlineKeyboardButton(config.ABOUT_BTN_INLINE, callback_data="about_callback")
    support_btn = telebot.types.InlineKeyboardButton(config.SUPPORT_BTN_INLINE, callback_data="support_callback")
    reviews_btn = telebot.types.InlineKeyboardButton(config.REVIEWS_BTN_INLINE, url=config.REVIEW_LINK)
    useful_btn = telebot.types.InlineKeyboardButton(config.USEFUL_BTN_INLINE, callback_data="useful_callback")
    markup.row(find_project_btn)
    markup.row(about_btn, support_btn)
    markup.row(reviews_btn, useful_btn)
    return markup


def get_about_inline_keyboard():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    faq_btn = telebot.types.InlineKeyboardButton(config.OPEN_FAQ_BTN_INLINE, url=config.FAQ_LINK)
    news_and_updates_btn = telebot.types.InlineKeyboardButton(config.NEWS_AND_UPDATES_BTN_INLINE, url=config.NEWS_AND_UPDATES_LINK)
    back_btn = telebot.types.InlineKeyboardButton(config.BACK_BTN_INLINE, callback_data="main_menu")
    markup.row(faq_btn)
    markup.row(news_and_updates_btn)
    markup.row(back_btn)
    return markup


def contact_support_inline_keyboard():
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    contact_support_btn = telebot.types.InlineKeyboardButton(config.CONTACT_SUPPORT_BTN_INLINE, url=config.CONTACT_SUPPORT_LINK)
    back_btn = telebot.types.InlineKeyboardButton(config.BACK_BTN_INLINE, callback_data="main_menu")
    markup.row(contact_support_btn)
    markup.row(back_btn)
    return markup


def useful_inline_keyboard():
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    directory_open_btn = telebot.types.InlineKeyboardButton(config.DIRECTORY_OPEN_BTN_INLINE, url=config.DIRECTORY_OPEN_LINK)
    back_btn = telebot.types.InlineKeyboardButton(config.BACK_BTN_INLINE, callback_data="main_menu")
    markup.row(directory_open_btn)
    markup.row(back_btn)
    return markup


def choose_category_markup():
    markup_categories = telebot.types.InlineKeyboardMarkup(row_width=2)
    categories = Category.objects.all()
    for category in categories:
        category_btn = telebot.types.InlineKeyboardButton(category.title, callback_data=f"choose_category#{category.id}")
        markup_categories.add(category_btn)
    back_btn = telebot.types.InlineKeyboardButton(config.BACK_BTN_INLINE, callback_data="main_menu")
    markup_categories.row(back_btn)
    return markup_categories


def get_currencies_keyboard(category):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    currencies = Currency.objects.filter(is_active=True)
    for currency in currencies:
        currency_btn = telebot.types.InlineKeyboardButton(f"{currency.title}", callback_data=f"choose_currency#{category.id}#{currency.id}")
        markup.add(currency_btn)

    back_btn = telebot.types.InlineKeyboardButton(config.BACK_BTN_INLINE, callback_data="find_project")
    markup.add(back_btn)
    return markup


def get_subscription_prices_markup(category, currency):
    markup_prices = telebot.types.InlineKeyboardMarkup(row_width=2)
    category_subscription_ids = CategorySubscription.objects.filter(category=category).values_list("subscription_id", flat=True)
    prices = SubscriptionPrice.objects.filter(currency=currency, subscription_id__in=category_subscription_ids)
    for price in prices:
        price_btn = telebot.types.InlineKeyboardButton(f"{price.price} {price.currency.title} / {price.subscription.title}", callback_data=f"choose_subscription_price#{price.id}")
        markup_prices.add(price_btn)

    back_btn = telebot.types.InlineKeyboardButton(config.BACK_BTN_INLINE, callback_data=f"choose_category#{category.id}")
    markup_prices.add(back_btn)

    return markup_prices


def get_payment_contact_markup(price):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn = telebot.types.InlineKeyboardButton(config.PAYMENT_CONTACT_BTN_TEXT, url=config.PAYMENT_CONTACT_URL)
    category_subscription = CategorySubscription.objects.filter(subscription=price.subscription).first()
    back_btn = telebot.types.InlineKeyboardButton(config.BACK_BTN_INLINE, callback_data=f"choose_currency#{category_subscription.category.id}#{price.currency.id}")
    markup.add(btn)
    markup.add(back_btn)
    return markup
