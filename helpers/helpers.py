import xlsxwriter
import datetime

from telegram import TelegramError

from DB import *
from config import XLSXFILES_PATH
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


def import_database():
    # Workbook() takes one, non-optional, argument
    # which is the filename that we want to create.
    document_name = datetime.datetime.now().strftime("users_and_orders_%d-%m-%Y_%H-%M-%S") + '.xlsx'
    workbook = xlsxwriter.Workbook(document_name)
    bold = workbook.add_format({'bold': True})

    # The workbook object is then used to add new
    # users_worksheet via the add_worksheet() method.
    users_worksheet = workbook.add_worksheet('users')

    fields_list = {"A1": "Ismi", "B1": "Telegram username", "C1": "Foydalanuvchi ID", "D1": "Ro'yxatdan o'tgan sana"}
    # Writing some data headers
    for key, value in fields_list.items():
        users_worksheet.write(key, value, bold)
    users_worksheet.set_column('A:D', 25)
    # Start from the first cell below the headers.
    row = 1

    # Use the users_worksheet object to write
    # data via the write() method.

    for user in get_all_users():
        selected_fields = [user[FULLNAME], user[USERNAME], user[ID], user['created_at'].strftime("%d-%m-%Y %X")]
        for col in range(len(selected_fields)):
            if selected_fields[col] is None:
                selected_fields[col] = 'None'
            users_worksheet.write(row, col, selected_fields[col])
        row += 1
    workbook.close()


import_database()
