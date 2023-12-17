import telebot
from constance import config

from bot.models import Category, Currency, Subscription, SubscriptionPrice, CategorySubscription


def main_menu_markup():
    markup_main = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=False)
    choose_category_btn = telebot.types.KeyboardButton(config.CHOOSE_CATEGORY_BTN_TEXT)
    get_subscription_btn = telebot.types.KeyboardButton(config.GET_SUBSCRIPTION_BTN_TEXT)
    about_btn = telebot.types.KeyboardButton(config.ABOUT_BTN_TEXT)
    help_btn = telebot.types.KeyboardButton(config.HELP_BTN_TEXT)

    markup_main.add(choose_category_btn)
    markup_main.add(get_subscription_btn)
    markup_main.add(about_btn)
    markup_main.add(help_btn)

    return markup_main


def choose_category_markup(callback_data="choose_category"):
    markup_categories = telebot.types.InlineKeyboardMarkup(row_width=2)
    categories = Category.objects.all()
    for category in categories:
        category_btn = telebot.types.InlineKeyboardButton(category.title, callback_data=f"{callback_data}#{category.id}")
        markup_categories.add(category_btn)

    return markup_categories


def get_subscriptions_by_category_markup(category):
    markup_subscriptions = telebot.types.InlineKeyboardMarkup(row_width=2)
    subscriptions = category.subscriptions.all()
    for subscription in subscriptions:
        currency_btn = telebot.types.InlineKeyboardButton(subscription.title, callback_data=f"choose_subscription#{subscription.id}")
        markup_subscriptions.add(currency_btn)

    return markup_subscriptions


def get_subscription_prices_markup(category, currency):
    markup_prices = telebot.types.InlineKeyboardMarkup(row_width=2)
    category_subscription_ids = CategorySubscription.objects.filter(category=category).values_list("subscription_id", flat=True)
    prices = SubscriptionPrice.objects.filter(currency=currency, subscription_id__in=category_subscription_ids)
    for price in prices:
        price_btn = telebot.types.InlineKeyboardButton(f"{price.price} {price.currency.title} / {price.subscription.title}", callback_data=f"choose_subscription_price#{price.id}")
        markup_prices.add(price_btn)

    back_btn = telebot.types.InlineKeyboardButton(config.BACK_BTN_TEXT_INLINE, callback_data=f"choose_category_for_subscription#{category.id}")
    markup_prices.add(back_btn)

    return markup_prices


def help_markup():
    markup_help = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=False)
    line_to_support_btn = telebot.types.KeyboardButton(config.LINE_TO_SUPPORT_BTN_TEXT)
    faq_btn = telebot.types.KeyboardButton(config.FAQ_BTN_TEXT)
    back_btn = telebot.types.KeyboardButton(config.BACK_BTN_TEXT)

    markup_help.add(line_to_support_btn)
    markup_help.add(faq_btn)
    markup_help.add(back_btn)

    return markup_help


def buy_subscription_to_choose_category():
    markup_subscription = telebot.types.ReplyKeyboardMarkup(True, one_time_keyboard=False)
    buy_subscription_btn = telebot.types.KeyboardButton(config.GET_SUBSCRIPTION_BTN_TEXT)
    back_btn = telebot.types.KeyboardButton(config.BACK_BTN_TEXT)

    markup_subscription.add(buy_subscription_btn)
    markup_subscription.add(back_btn)

    return markup_subscription


def get_payment_contact_markup():
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn = telebot.types.InlineKeyboardButton(config.PAYMENT_CONTACT_BTN_TEXT, url=config.PAYMENT_CONTACT_URL)
    markup.add(btn)
    return markup


def get_currencies_keyboard(category):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    currencies = Currency.objects.filter(is_active=True)
    for currency in currencies:
        currency_btn = telebot.types.InlineKeyboardButton(f"{currency.title}", callback_data=f"choose_currency#{category.id}#{currency.id}")
        markup.add(currency_btn)

    back_btn = telebot.types.InlineKeyboardButton(config.BACK_BTN_TEXT_INLINE, callback_data=f"choose_category_for_subscribe")
    markup.add(back_btn)
    return markup


def get_vacancy_footer_keyboard(author_username=None):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    if author_username:
        author_btn = telebot.types.InlineKeyboardButton(config.VACANCY_AUTHOR_BTN_INLINE, url=f"https://t.me/{author_username}")
        markup.add(author_btn)
    complaint_on_author_btn = telebot.types.InlineKeyboardButton(config.COMPLAINT_ON_AUTHOR_BTN_INLINE, url=f"https://t.me/{config.COMPLAINT_ACCOUNT_USERNAME}")
    markup.add(complaint_on_author_btn)
    return markup
