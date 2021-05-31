from telegram import TelegramError
from globalvariables import *


def wrap_tags(*args):
    symbol = ' ' if len(args) > 1 else ''
    return f'<b><i><u>{symbol.join(args)}</u></i></b>'


def delete_message_by_message_id(context, user):
    user_data = context.user_data

    if MESSAGE_ID in user_data:
        try:
            context.bot.delete_message(user[TG_ID], user_data[MESSAGE_ID])
        except TelegramError:
            try:
                context.bot.edit_message_reply_markup(user[TG_ID], user_data[MESSAGE_ID])
            except TelegramError:
                pass
        finally:
            user_data.pop(MESSAGE_ID)
