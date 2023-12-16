from bot.models import MessageStatus, Message
from bot.services.telebot_service.send_message import send_tg_message


def mass_send(message, users):
    count = 0
    errors = 0

    message_text = message.text

    parse_mode = {}
    if message.parse_mode == "yes":
        parse_mode = {"parse_mode": "MarkdownV2"}

    for user in users:
        if user not in message.recipients.all():
            message.recipients.add(user)
        try:
            file = Message.objects.get(id=message.id).loaded_file
            send_tg_message(
                text=message_text,
                chat_id=user.chat_id,
                message_type=message.message_type,
                file=file,
                file_id=message.loaded_file_id,
                parse_mode=parse_mode
            )

        except Exception as e:
            status_message = MessageStatus.objects.filter(message=message, user=user)[0]
            status_message.status = MessageStatus.STATUS_ERROR
            status_message.error = e
            status_message.save()
            errors += 1
        else:
            status_message = MessageStatus.objects.filter(message=message, user=user)[0]
            status_message.status = MessageStatus.STATUS_SENT
            status_message.error = None
            status_message.save()
            count += 1

    return count, errors
