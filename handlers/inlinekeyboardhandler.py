from telegram.ext import CallbackQueryHandler, CallbackContext
from telegram import Update, ParseMode, InlineKeyboardMarkup
from helpers import wrap_tags
from helpers import set_user_data
from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from globalvariables import *
from DB import *
from config import ADMIN
import json
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logger = logging.getLogger()


def inline_keyboards_handler_callback(update: Update, context: CallbackContext):
    # with open('jsons/callback_query.json', 'w') as callback_query_file:
    #     callback_query_file.write(callback_query.to_json())
    user_data = context.user_data
    set_user_data(update.effective_user.id, user_data)
    user = user_data['user_data']

    callback_query = update.callback_query
    data = callback_query.data

    if user[TG_ID] == ADMIN:

        match_obj = re.search(r'^[rc]_\d+$', data)
        match_obj_2 = re.search(r'[rc]_[yn]_\d+$', data)
        match_obj_3 = re.search(r'^w_\d+$', data)

        new_text = ''

        if match_obj or match_obj_2:

            if match_obj:
                data = match_obj.string.split('_')
                keyboard = choose_keyboard

            elif match_obj_2:
                data = match_obj_2.string.split('_')
                order = get_order(data[-1])

                geo = json.loads(order[GEOLOCATION]) if order[GEOLOCATION] else None

                if data[1] == 'n':
                    keyboard = orders_keyboard
                    data = [geo, data[-1]]

                elif data[1] == 'y':
                    status = 'canceled' if data[0] == 'c' else 'received'
                    update_result = update_order_status(status, data[-1])

                    if update_result == 'updated':
                        client_text = 'Buyurtma rad qilindi' if status == 'canceled' else 'Buyurtma qabul qilindi'
                        client_text = wrap_tags(client_text) + f' [\U0001F194 {order["id"]}]'

                        context.bot.send_message(order[USER_TG_ID], client_text,
                                                 parse_mode=ParseMode.HTML, reply_to_message_id=order[MESSAGE_ID])

                    data, keyboard = (geo, geo_keyboard) if geo else (None, None)

                    status_text = 'rad etilgan' if status == 'canceled' else 'qabul qilingan'
                    new_text = callback_query.message.text.split('\n')
                    new_text[0] = ' '.join(new_text[0].split()[:2])
                    new_text[-1] = f'Status: {wrap_tags(status_text)}'
                    new_text = '\n'.join(new_text)

            callback_query.answer()

            if new_text:
                if keyboard:
                    inline_keyboard = InlineKeyboard(keyboard, user[LANG], data=data).get_keyboard()
                else:
                    inline_keyboard = None

                callback_query.edit_message_text(new_text, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
            else:
                inline_keyboard = InlineKeyboard(keyboard, user[LANG], data=data).get_keyboard()
                callback_query.edit_message_reply_markup(inline_keyboard)

        elif match_obj_3:
            received_orders = get_orders_by_status(status='received')
            wanted = int(data.split('_')[-1])
            order = received_orders[wanted - 1]
            order_itmes = get_order_items(order['id'])
            new_dict = dict()

            for item in order_itmes:
                new_dict.update({item['book_id']: item['quantity']})

            books_ids = [str(item['book_id']) for item in order_itmes]
            books = get_books(books_ids)
            books_text = ''

            for book in books:
                books_text += f'Kitob nomi: {book["title"]}\n' \
                              f'Soni: {new_dict[book["id"]]}\n' \
                              f'------------------\n'
            inline_keyboard = InlineKeyboard(paginate_keyboard, user[LANG], data=[wanted, received_orders]) \
                .get_keyboard()

            if order[GEOLOCATION]:
                geo = json.loads(order[GEOLOCATION])
                inline_keyboard = inline_keyboard.inline_keyboard
                keyboard = InlineKeyboard(geo_keyboard, data=geo).get_keyboard().inline_keyboard
                inline_keyboard += keyboard
                inline_keyboard = InlineKeyboardMarkup(inline_keyboard)

            received_user = get_user(order['user_id'])

            text = [
                f'\U0001F194 {order["id"]}',
                f'Status: {wrap_tags(order["status"])}',
                f'Yaratilgan vaqti: {order["created_at"].strftime("%d-%m-%Y %X")}',
                f'Tel: {order["phone_number"]}',
                f'Manzil: {order["address"]}',
                f'Ism: {received_user["fullname"]}',
            ]

            if received_user["username"]:
                text = text + [f'Telegram: @{received_user["username"]}']

            text = '\n'.join(text)
            text += f'\n\n{books_text}'
            # print(inline_keyboard)
            # print(received_user)
            # print(order)
            # exit()
            callback_query.answer()
            callback_query.edit_message_text(text, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
        else:
            callback_query.answer()

    else:
        match_obj = re.search(r'^w_\d+$', data)
        callback_query.answer()

        if match_obj:
            wanted = int(match_obj.string.split('_')[-1])
            user_orders = get_user_orders(user[ID])
            order = user_orders[wanted - 1]
            order_itmes = get_order_items(order['id'])
            new_dict = dict()
            books_ids = []
            books_text = ''

            for item in order_itmes:
                new_dict.update({item['book_id']: item['quantity']})
                books_ids += [str(item['book_id'])]

            books = get_books(books_ids)
            for book in books:
                books_text += f'Kitob nomi: {wrap_tags(book["title"])}\n' \
                              f'Soni: {wrap_tags(str(new_dict[book["id"]]) + " ta")}' \
                              f'\n{wrap_tags("".ljust(22, "-"))}\n'

            status = 'qabul qilingan' if order["status"] == 'received' else 'rad etilgan' \
                if order["status"] == 'canceled' else 'yetkazilgan'
            text = [
                f'\U0001F194 {order["id"]}',
                f'Status: {wrap_tags(status)}',
                f'Yaratilgan vaqti: {wrap_tags(order["created_at"].strftime("%d-%m-%Y %X"))}'
            ]
            text = '\n'.join(text)
            text += f'\n\n{books_text}'

            inline_keyboard = InlineKeyboard(paginate_keyboard, user[LANG], data=[wanted, user_orders]) \
                .get_keyboard()
            callback_query.edit_message_text(text, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

    # logger.info('user_data: %s', user_data)


inline_keyboard_handler = CallbackQueryHandler(inline_keyboards_handler_callback)
