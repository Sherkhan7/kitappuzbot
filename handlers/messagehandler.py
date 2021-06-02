import ujson

from telegram.ext import Filters, MessageHandler, CallbackContext
from telegram import Update, InlineKeyboardMarkup

from DB import *
from globalvariables import *
from config import *
from layouts import *
from helpers import wrap_tags, import_database

from replykeyboards.replykeyboardtypes import reply_keyboard_types
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *


def message_handler_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    full_text = update.message.text
    text = full_text.split(' ', 1)[-1]

    if user:
        if user[IS_ADMIN]:
            # Yangi buyurtmalar
            if text == reply_keyboard_types[admin_menu_keyboard][0][f'text_{user[LANG]}']:
                waiting_orders = get_orders_by_status(status='waiting')
                if waiting_orders:
                    for order in waiting_orders:
                        order_itmes = get_order_items(order[ID])
                        client = get_user(order[USER_ID])
                        geo = ujson.loads(order[GEOLOCATION]) if order[GEOLOCATION] else None
                        new_dict = dict()
                        label = '[Yangi buyurtma]'

                        for item in order_itmes:
                            new_dict.update({item['book_id']: item['quantity']})

                        text_for_admin = f'\U0001F194 {order[ID]} '

                        if order['with_action']:
                            text_for_admin += get_action_layout(new_dict)
                        else:
                            text_for_admin += get_basket_layout(new_dict, user[LANG], data=label)

                        text_for_admin += f'\nMijoz: {wrap_tags(client[FULLNAME])}\n' \
                                          f'Tel: {wrap_tags(order[PHONE_NUMBER])}\n'
                        # f'Manzil: {wrap_tags(order[ADDRESS])}\n'
                        text_for_admin += f'Telegram: {wrap_tags("@" + client[USERNAME])}\n' \
                            if client[USERNAME] else '\n'
                        text_for_admin += f'Status: {wrap_tags("qabul qilish kutilmoqda")}'
                        inline_keyboard = InlineKeyboard(orders_keyboard, user[LANG], [geo, order[ID]]).get_keyboard()
                        update.message.reply_text(text_for_admin, reply_markup=inline_keyboard)

                else:
                    update.message.reply_text('Yangi buyurtmalar mavjud emas !')

            # Qabul qilingan buyutmalar or Tarix
            if text == reply_keyboard_types[admin_menu_keyboard][1][f'text_{user[LANG]}'] or \
                    (text == reply_keyboard_types[admin_menu_keyboard][2][f'text_{user[LANG]}']):

                if text == reply_keyboard_types[admin_menu_keyboard][2][f'text_{user[LANG]}']:
                    orders = get_orders_by_status(('delivered', 'canceled'))
                    empty_text = "Tarix  bo'sh !"
                    label = '[Tarix]'
                    history = True
                else:
                    orders = get_orders_by_status('received')
                    empty_text = 'Qabul qilingan buyurtmalar mavjud emas !'
                    label = ''
                    history = None

                if orders:
                    wanted = 1
                    order = orders[wanted - 1]
                    status = 'yetkazilgan' if order[STATUS] == 'delivered' else 'rad etilgan' \
                        if order[STATUS] == 'canceled' else 'qabul qilingan'
                    client = get_user(order[USER_ID])
                    order_itmes = get_order_items(order[ID])
                    new_dict = dict()
                    books_ids = []
                    books_text = ''

                    for item in order_itmes:
                        new_dict.update({item['book_id']: item['quantity']})
                        books_ids += [str(item['book_id'])]

                    books = get_books(books_ids)
                    for index, book in enumerate(books):
                        books_text += f'{index + 1}) Kitob nomi: {wrap_tags(book[TITLE])}\n' \
                                      f'Soni: {wrap_tags(str(new_dict[book[ID]]) + " ta")}\n' \
                                      f'{"_" * 22}\n\n'

                    inline_keyboard = InlineKeyboard(paginate_keyboard, user[LANG], data=[wanted, orders],
                                                     history=history).get_keyboard()

                    if order[GEOLOCATION]:
                        geo = ujson.loads(order[GEOLOCATION])
                        inline_keyboard = inline_keyboard.inline_keyboard
                        keyboard = InlineKeyboard(geo_keyboard, data=geo).get_keyboard().inline_keyboard
                        inline_keyboard += keyboard
                        inline_keyboard = InlineKeyboardMarkup(inline_keyboard)

                    text = [
                        f'\U0001F194 {order[ID]} {label}\n',
                        f'Status: {wrap_tags(status)}',
                        f'Yaratilgan vaqti: {wrap_tags(order["created_at"].strftime("%d-%m-%Y %X"))}\n',
                        f'Ism: {wrap_tags(client[FULLNAME])}',
                        f'Tel: {wrap_tags(order[PHONE_NUMBER])}',
                        f'Telegram: {wrap_tags("@" + client[USERNAME])}' if client[USERNAME] else ''
                        # f'Manzil: {order["address"]}',
                    ]
                    text = '\n'.join(text)
                    text += f'\n\n{books_text}'
                    update.message.reply_text(text, reply_markup=inline_keyboard)

                else:
                    update.message.reply_text(empty_text)

            # Bazani yuklash
            if text == reply_keyboard_types[admin_menu_keyboard][3][f'text_{user[LANG]}']:
                context.bot.send_chat_action(user[TG_ID], 'upload_document')
                full_path = import_database()
                with open(full_path, 'rb') as file:
                    update.message.reply_document(file)

        else:
            # Buyrutmalarim
            if text == reply_keyboard_types[client_menu_keyboard][2][f'text_{user[LANG]}']:
                user_orders = get_user_orders(user[ID])

                if user_orders:
                    wanted = 1
                    order = user_orders[wanted - 1]
                    order_itmes = get_order_items(order[ID])
                    new_dict = dict()
                    books_ids = []
                    books_text = ''
                    label = ''
                    if order['with_action']:
                        label += "[🔥MEGA AKSIYA🔥]"

                    for item in order_itmes:
                        new_dict.update({item['book_id']: item['quantity']})
                        books_ids += [str(item['book_id'])]

                    books = get_books(books_ids)
                    for book in books:
                        books_text += f'Kitob nomi: {wrap_tags(book[TITLE])}\n' \
                                      f'Soni: {wrap_tags(str(new_dict[book[ID]]) + " ta")}\n' \
                                      f'{"_" * 22}\n\n'

                    status = 'qabul qilingan' if order[STATUS] == 'received' else 'rad etilgan' \
                        if order[STATUS] == 'canceled' else 'qabul qilish kutilmoqda' \
                        if order[STATUS] == 'waiting' else 'yetkazilgan'
                    text = [
                        f'\U0001F194 {order[ID]} {label}\n',
                        f'Status: {wrap_tags(status)}',
                        f'Yaratilgan vaqti: {wrap_tags(order["created_at"].strftime("%d-%m-%Y %X"))}'
                    ]
                    text = '\n'.join(text)
                    text += f'\n\n{books_text}'
                    inline_keyboard = InlineKeyboard(paginate_keyboard, user[LANG],
                                                     [wanted, user_orders]).get_keyboard()

                    if order[STATUS] == 'received':
                        deliv_keyb = InlineKeyboard(delivery_keyboard, user[LANG], data=order[ID]).get_keyboard()
                        pag_keyb = inline_keyboard.inline_keyboard
                        deliv_keyb = deliv_keyb.inline_keyboard
                        inline_keyboard = InlineKeyboardMarkup(pag_keyb + deliv_keyb)
                    update.message.reply_text(text, reply_markup=inline_keyboard)

                else:
                    update.message.reply_text('Sizda hali buyurtmalar mavjud emas !')

            # Biz ijtimoiy tarmoqlarda
            elif text == reply_keyboard_types[client_menu_keyboard][3][f'text_{user[LANG]}']:
                inline_keyboard = InlineKeyboard(social_medias_keyboard, user[LANG]).get_keyboard()
                update.message.reply_photo(PHOTOS_URL + 'kitappuz_photo.jpg', reply_markup=inline_keyboard)

            # Biz bilan bo'glanish
            elif text == reply_keyboard_types[client_menu_keyboard][4][f'text_{user[LANG]}']:
                text = f"Kitapp premium adminlari bilan boglanish uchun:\n" \
                       f"{wrap_tags('@kitapp_admin', '[ +998999131099 ]')} ga murojaat qilishingiz mumkin."
                update.message.reply_text(text)

            else:
                thinking_emoji = '🤔'
                update.message.reply_text(thinking_emoji, quote=True)

    else:
        reply_text = "🔴 Siz ro'yxatdan o'tmagansiz !\nBuning uchun /start ni bosing"
        # "\U000026A0 Сиз рўйхатдан ўтмагансиз !\nБунинг учун /start ни босинг"
        update.message.reply_text(reply_text)


message_handler = MessageHandler(Filters.text & (~ Filters.command & ~Filters.update.edited_message),
                                 message_handler_callback)
