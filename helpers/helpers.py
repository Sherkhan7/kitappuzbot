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
    full_path = XLSXFILES_PATH + document_name
    workbook = xlsxwriter.Workbook(full_path)
    bold = workbook.add_format({'bold': True})

    # The workbook object is then used to add new
    # users_worksheet via the add_worksheet() method.
    users_worksheet = workbook.add_worksheet('users')
    orders_worksheet = workbook.add_worksheet('orders')

    # Writing some data headers
    def write_data_headers(worksheet, data):
        for key, value in data.items():
            worksheet.write(key, value['header'], bold)
            worksheet.set_column(f'{key[0]}:{key[0]}', value['with'])

    user_fields_list = {
        "A1": {
            "header": "ID",
            "with": 5,
        },
        "B1": {
            "header": "Ismi",
            "with": 25,
        },
        "C1": {
            "header": "Telegram username",
            "with": 25,
        },
        "D1": {
            "header": "Ro'yxatdan o'tgan sana",
            "with": 25
        }
    }
    orders_fields_list = {
        "A1": {
            "header": "#",
            "with": 5,
        },
        "B1": {
            "header": "Ismi",
            "with": 25,
        },
        "C1": {
            "header": "Tel",
            "with": 15
        },
        "D1": {
            "header": "Telegram username",
            "with": 25,
        },
        "E1": {
            "header": "Buyurtma qilgan kitoplari",
            "with": 35,
        },
        "F1": {
            "header": "Buyurtma summasi (so'm)",
            "with": 25
        },
        "G1": {
            "header": "Buyurtma statusi",
            "with": 20
        },
        "H1": {
            "header": "Aksiya",
            "with": 15
        },
        "I1": {
            "header": "Buyurtma sanasi",
            "with": 25
        },

    }

    write_data_headers(users_worksheet, user_fields_list)
    write_data_headers(orders_worksheet, orders_fields_list)
    row = 1
    # Use the users_worksheet object to write
    # data via the write() method.
    for user in get_all_users():
        selected_fields = [
            user[ID],
            user[FULLNAME],
            user[USERNAME],
            user['created_at'].strftime("%d-%m-%Y %X")
        ]
        for col in range(len(selected_fields)):
            if selected_fields[col] is None:
                selected_fields[col] = 'None'
            users_worksheet.write(row, col, selected_fields[col])
        row += 1

    row = 1
    # Use the users_worksheet object to write
    # data via the write() method.
    for order in get_all_orders():
        user = get_user(order[USER_TG_ID])
        order_items = get_order_items(order[ID])
        books_str = ''
        summa = 0
        action = 'None' if not order['with_action'] else 'Mega aksiya'
        status = 'Yetkazilgan' if order[STATUS] == 'delivered' else 'Bekor qilingan' if order[STATUS] == 'canceled' \
            else 'Qabul qilingan' if order[STATUS] == 'received' else 'Qaubul qilish kutilmoqda'
        for order_item in order_items:
            book = get_book(order_item['book_id'])
            books_str += f"{book[TITLE]}: {order_item['quantity']} ta\n" \
                         f"Narxi: {book[PRICE]:,} so'm\n" \
                         f"{'-' * 10}\n"
            summa += book[PRICE] * order_item['quantity']
        summa = f'{summa:,}'.replace(',', ' ')
        selected_fields = [
            order[ID],
            user[FULLNAME],
            order[PHONE_NUMBER],
            user[USERNAME],
            books_str.replace(',', ' '),
            summa,
            status,
            action,
            order['created_at'].strftime("%d-%m-%Y %X"),

        ]
        for col in range(len(selected_fields)):
            if selected_fields[col] is None:
                selected_fields[col] = 'None'
            orders_worksheet.write(row, col, selected_fields[col])
        orders_worksheet.set_row(row, 60)
        row += 1

    workbook.close()
    return full_path
