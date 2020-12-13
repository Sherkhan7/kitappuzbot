from telegram.ext import Filters, MessageHandler, CallbackContext
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from helpers import set_user_data
from replykeyboards.replykeyboardtypes import reply_keyboard_types
from replykeyboards.replykeyboardvariables import *
from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from globalvariables import *
from layouts import get_basket_layout
from DB import *
from helpers import wrap_tags
import json


def message_handler_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user_data = context.user_data
    set_user_data(update.effective_user.id, user_data)
    user = user_data['user_data']

    full_text = update.message.text
    text = full_text.split(' ', 1)[-1]

    if user:

        if user[IS_ADMIN]:

            if text == reply_keyboard_types[admin_menu_keyboard][user[LANG]][2]:

                received_orders = get_orders_by_status(status='received')

                if received_orders:
                    wanted = 1
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
                        f'Yaratilgan sana: {order["created_at"].strftime("%d-%m-%Y %X")}',
                        f'Tel: {order["phone_number"]}',
                        f'Manzil: {order["address"]}',
                        f'Ism: {received_user["fullname"]}',
                    ]
                    if received_user["username"]:
                        text = text + [f'Telegram: @{received_user["username"]}']
                    text = '\n'.join(text)
                    text += f'\n\n{books_text}'
                    # print(inline_keyboard)
                    # print(received_orders)
                    # exit()
                    update.message.reply_text(text, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

                else:
                    update.message.reply_text('Qabul qilingan buyurtmalar mavjud emas !')

            if text == reply_keyboard_types[admin_menu_keyboard][user[LANG]][1]:
                waiting_orders = get_orders_by_status(status='waiting')

                if waiting_orders:

                    for order in waiting_orders:
                        order_itmes = get_order_items(order['id'])
                        ordred_user = get_user(order[USER_ID])
                        geo = json.loads(order[GEOLOCATION]) if order[GEOLOCATION] else None

                        new_dict = dict()
                        data = f'\U0001F194 {order["id"]} [Yangi buyurtma]'

                        for item in order_itmes:
                            new_dict.update({item['book_id']: {'quantity': item['quantity']}})

                        text_for_admin = get_basket_layout(new_dict, user[LANG], data=data)
                        text_for_admin += f'\nMijoz: {wrap_tags(ordred_user[FULLNAME])}\n' \
                                          f'Manzil: {wrap_tags(order[ADDRESS])}\n' \
                                          f'Tel: {order[PHONE_NUMBER]}\n'

                        text_for_admin += f'Telegram: @{ordred_user[USERNAME]}' if ordred_user[USERNAME] else ''
                        text_for_admin += f'\nStatus: {order[STATUS]}'

                        inline_keyboard = InlineKeyboard(orders_keyboard, user[LANG],
                                                         data=[geo, order['id']]).get_keyboard()

                        update.message.reply_text(text_for_admin, reply_markup=inline_keyboard,
                                                  parse_mode=ParseMode.HTML)
                else:
                    update.message.reply_text('Yangi buyurtmalar mavjud emas !')

        else:
                                       
            if text == reply_keyboard_types[user_menu_keyboard][user[LANG]][2]:
                user_orders = get_user_orders(user[ID])

                if user_orders:
                    wanted = 1
                    order = user_orders[wanted - 1]
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

                    inline_keyboard = InlineKeyboard(paginate_keyboard, user[LANG], data=[wanted, user_orders]) \
                        .get_keyboard()
                    text = [
                        f'\U0001F194 {order["id"]}',
                        f'Status: {wrap_tags(order["status"])}',
                        f'Yaratilgan sana: {order["created_at"].strftime("%d-%m-%Y %X")}'
                    ]
                    text = '\n'.join(text)
                    text += f'\n\n{books_text}'
                    # print(inline_keyboard.to_dict())
                    update.message.reply_text(text, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

                else:
                    update.message.reply_text('Sizda hali buyurtmalar mavjud emas !')

            elif text == reply_keyboard_types[client_menu_keyboard][user[LANG]][3]:
                update.message.reply_text("Biz bilan bog;lanish uchun: +998 XX XXXXXXX ga go'qngiroq qiling")

            else:
                thinking_emoji = '\U0001F914'
                update.message.reply_text(thinking_emoji, quote=True)

    else:

        reply_text = "\U000026A0 Siz ro'yxatdan o'tmagansiz !\nBuning uchun /start ni bosing."
        # "\U000026A0 Вы не зарегистрированы !\nДля этого нажмите /start\n\n" \
        # "\U000026A0 Сиз рўйхатдан ўтмагансиз !\nБунинг учун /start ни босинг"

        update.message.reply_text(reply_text)


message_handler = MessageHandler(Filters.text & (~ Filters.command), message_handler_callback)
