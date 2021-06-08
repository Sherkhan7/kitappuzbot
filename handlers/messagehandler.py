import ujson
import re

from telegram.ext import Filters, MessageHandler, CallbackContext
from telegram import Update, InlineKeyboardMarkup

from DB import *
from globalvariables import *
from config import *
from layouts import *
from helpers import wrap_tags, import_database

from replykeyboards.replykeyboardvariables import *
from replykeyboards.replykeyboardtypes import reply_keyboard_types

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *


def message_handler_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)

    if user:
        new_orders_btn = reply_keyboard_types[admin_menu_keyboard]['new_orders_btn'][f'text_{user[LANG]}']
        received_orders_btn = reply_keyboard_types[admin_menu_keyboard]['received_orders_btn'][f'text_{user[LANG]}']
        history_btn = reply_keyboard_types[admin_menu_keyboard]['history_btn'][f'text_{user[LANG]}']
        download_database_btn = reply_keyboard_types[admin_menu_keyboard]['download_database_btn'][f'text_{user[LANG]}']
        my_orders_btn = reply_keyboard_types[client_menu_keyboard]['my_orders_btn'][f'text_{user[LANG]}']
        social_nets_btn = reply_keyboard_types[client_menu_keyboard]['social_nets_btn'][f'text_{user[LANG]}']
        contact_us_btn = reply_keyboard_types[client_menu_keyboard]['contact_us_btn'][f'text_{user[LANG]}']

        if user[IS_ADMIN]:
            # Yangi buyurtmalar
            if re.search(f'{new_orders_btn}$', update.message.text):
                waiting_orders = get_orders_by_status(status='waiting')
                if waiting_orders:
                    for order in waiting_orders:
                        order_items = get_order_items_book_title(order[ID])
                        client = get_user(order[USER_ID])
                        geo = ujson.loads(order[GEOLOCATION]) if order[GEOLOCATION] else None
                        new_dict = dict()
                        label = '[Yangi buyurtma]'

                        for item in order_items:
                            new_dict.update({item['book_id']: item['quantity']})

                        text_for_admin = f'🆔 {order[ID]} '

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
                return

                # Qabul qilingan buyutmalar or Tarix
            elif re.search(f'({received_orders_btn}|{history_btn})$', update.message.text):
                if re.search(f'{history_btn}$', update.message.text):
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
                    order_items = get_order_items_book_title(order[ID])
                    books_layout = get_books_layout(order, order_items, client, {STATUS: status, 'label': label})
                    inline_keyboard = InlineKeyboard(paginate_keyboard, user[LANG], data=[wanted, orders],
                                                     history=history).get_keyboard()
                    # if order[GEOLOCATION]:
                    #     geo = ujson.loads(order[GEOLOCATION])
                    #     inline_keyboard = inline_keyboard.inline_keyboard
                    #     keyboard = InlineKeyboard(geo_keyboard, data=geo).get_keyboard().inline_keyboard
                    #     inline_keyboard += keyboard
                    #     inline_keyboard = InlineKeyboardMarkup(inline_keyboard)

                    update.message.reply_text(books_layout, reply_markup=inline_keyboard)

                else:
                    update.message.reply_text(empty_text)
                return

            # Bazani yuklash
            elif re.search(f'{download_database_btn}$', update.message.text):
                context.bot.send_chat_action(user[TG_ID], 'upload_document')
                with open(import_database(), 'rb') as file:
                    update.message.reply_document(file)
                return
            else:
                thinking_emoji = '🤔🤔'
                update.message.reply_text(thinking_emoji, quote=True)
                return

        else:
            # Buyrutmalarim
            if re.search(f'{my_orders_btn}$', update.message.text):
                user_orders = get_user_orders(user[ID])

                if user_orders:
                    wanted = 1
                    order = user_orders[wanted - 1]
                    order_items = get_order_items_book_title(order[ID])
                    label = ''
                    if order['with_action']:
                        label += "[🔥MEGA AKSIYA🔥]"

                    status = 'qabul qilingan' if order[STATUS] == 'received' else 'rad etilgan' \
                        if order[STATUS] == 'canceled' else 'qabul qilish kutilmoqda' \
                        if order[STATUS] == 'waiting' else 'yetkazilgan'
                    get_order_items_book_title(order[ID])
                    books_layout = get_books_layout(order, order_items, user, {STATUS: status, 'label': label})
                    inline_keyboard = InlineKeyboard(paginate_keyboard, user[LANG],
                                                     [wanted, user_orders]).get_keyboard()
                    if order[STATUS] == 'received':
                        deliv_keyb = InlineKeyboard(delivery_keyboard, user[LANG], data=order[ID]).get_keyboard()
                        pag_keyb = inline_keyboard.inline_keyboard
                        deliv_keyb = deliv_keyb.inline_keyboard
                        inline_keyboard = InlineKeyboardMarkup(pag_keyb + deliv_keyb)

                    update.message.reply_text(books_layout, reply_markup=inline_keyboard)

                else:
                    update.message.reply_text('Sizda hali buyurtmalar mavjud emas !')
                return

            # Biz ijtimoiy tarmoqlarda
            elif re.search(f'{social_nets_btn}$', update.message.text):
                inline_keyboard = InlineKeyboard(social_medias_keyboard, user[LANG]).get_keyboard()
                update.message.reply_photo(PHOTOS_URL + 'kitappuz_photo.jpg', reply_markup=inline_keyboard)
                return

            # Biz bilan bo'glanish
            elif re.search(f'{contact_us_btn}$', update.message.text):
                text = f"Kitapp premium adminlari bilan boglanish uchun:\n" \
                       f"{wrap_tags('@kitapp_admin', '[ +998999131099 ]')} ga murojaat qilishingiz mumkin."
                update.message.reply_text(text)
                return

            else:
                thinking_emoji = '🤔🤔'
                update.message.reply_text(thinking_emoji, quote=True)
                return

    else:
        reply_text = "🔴 Siz ro'yxatdan o'tmagansiz !\nBuning uchun /start ni bosing"
        # "\U000026A0 Сиз рўйхатдан ўтмагансиз !\nБунинг учун /start ни босинг"
        update.message.reply_text(reply_text)
        return


message_handler = MessageHandler(Filters.text & (~ Filters.command & ~Filters.update.edited_message),
                                 message_handler_callback)
