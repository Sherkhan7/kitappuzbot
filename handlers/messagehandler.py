import re

from telegram.ext import Filters, MessageHandler, CallbackContext
from telegram import Update, InlineKeyboardMarkup

from DB import *
from globalvariables import *
from config import *
from layouts import *
from helpers import wrap_tags, import_database

from replykeyboards import ReplyKeyboard
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
        edit_bot_btn = reply_keyboard_types[admin_menu_keyboard]['edit_bot_btn'][f'text_{user[LANG]}']
        back_btn = reply_keyboard_types[edit_bot_keyboard]['back_btn'][f'text_{user[LANG]}']

        if user[IS_ADMIN]:
            # Yangi buyurtmalar
            if re.search(f'{new_orders_btn}$', update.message.text):
                waiting_orders = get_orders_by_status('waiting')

                if waiting_orders:
                    for order in waiting_orders:
                        client = get_user(order[USER_ID])
                        order_items = get_order_items_book_title(order[ID])
                        label = wrap_tags('[Yangi buyurtma]')

                        if order_items:
                            new_dict = dict()
                            if order['with_action']:
                                label = f'[🔥MEGA AKSIYA🔥] {label}'

                            for item in order_items:
                                new_dict.update({item['book_id']: item['quantity']})
                            layout = get_basket_layout(new_dict, user[LANG], '')
                        else:
                            if order['with_action'] and order['action_id']:
                                action = get_action(order['action_id'])
                                label = f"[ {action[TITLE]} ] {label}"
                                layout = f"{action['text']}\n"

                        text_for_admin = f'🆔 {order[ID]} {label}\n\n'
                        text_for_admin += layout
                        text_for_admin += f'\nMijoz: {wrap_tags(client[FULLNAME])}\n' \
                                          f'Tel: {wrap_tags(order[PHONE_NUMBER])}\n'
                        text_for_admin += f'Telegram: {wrap_tags("@" + client[USERNAME])}\n' \
                            if client[USERNAME] else '\n'
                        text_for_admin += f'Status: {wrap_tags("qabul qilish kutilmoqda")}'
                        inline_keyb_markup = InlineKeyboard(orders_keyboard, user[LANG], order[ID]).get_markup()
                        update.message.reply_text(text_for_admin, reply_markup=inline_keyb_markup)

                else:
                    update.message.reply_text('Yangi buyurtmalar mavjud emas !')
                return

            # Qabul qilingan buyurtmalar va Tarrix
            elif re.search(f'({received_orders_btn}|{history_btn})$', update.message.text):
                if re.search(f'{history_btn}$', update.message.text):
                    orders = get_orders_by_status('delivered', 'canceled')
                    empty_text = "Tarix  bo'sh !"
                    history = True
                    label = '[Tarix]'
                else:
                    orders = get_orders_by_status('received')
                    empty_text = 'Qabul qilingan buyurtmalar mavjud emas !'
                    history = None
                    label = ''

                if orders:
                    wanted = 1
                    order = orders[wanted - 1]
                    client = get_user(order[USER_ID])
                    status = 'yetkazilgan' if order[STATUS] == 'delivered' else 'rad etilgan' \
                        if order[STATUS] == 'canceled' else 'qabul qilingan'
                    order_items = get_order_items_book_title(order[ID])
                    books_layout = get_books_layout(order, order_items, client, {STATUS: status, 'label': label})
                    inline_keyb_markup = InlineKeyboard(paginate_keyboard, user[LANG], [wanted, orders],
                                                        history).get_markup()
                    update.message.reply_text(books_layout, reply_markup=inline_keyb_markup)

                else:
                    update.message.reply_text(empty_text)
                return

            # Bazani yuklash
            elif re.search(f'{download_database_btn}$', update.message.text):
                context.bot.send_chat_action(user[TG_ID], 'upload_document')
                with open(import_database(), 'rb') as file:
                    update.message.reply_document(file)
                return

            # Botni tahrirlash
            elif re.search(f'{edit_bot_btn}$', update.message.text):
                reply_keyb_markupoard = ReplyKeyboard(edit_bot_keyboard, user[LANG]).get_markup()
                update.message.reply_text(update.message.text, reply_markup=reply_keyb_markupoard)
                return

            # « Ortga
            elif re.search(f'{back_btn}$', update.message.text):
                reply_keyb_markupoard = ReplyKeyboard(admin_menu_keyboard, user[LANG]).get_markup()
                update.message.reply_text(update.message.text, reply_markup=reply_keyb_markupoard)
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
                    label = "[🔥MEGA AKSIYA🔥]" if order['with_action'] else ''
                    status = 'qabul qilingan' if order[STATUS] == 'received' else 'rad etilgan' \
                        if order[STATUS] == 'canceled' else 'qabul qilish kutilmoqda' if order[STATUS] == 'waiting' \
                        else 'yetkazilgan'
                    books_layout = get_books_layout(order, order_items, user, {STATUS: status, 'label': label})
                    inline_keyb_markup = InlineKeyboard(paginate_keyboard, user[LANG],
                                                        [wanted, user_orders]).get_markup()

                    if order[STATUS] == 'received':
                        delivery_keyb = InlineKeyboard(delivery_keyboard, user[LANG], order[ID]).get_markup()
                        delivery_keyb_list = delivery_keyb.inline_keyboard
                        paginate_keyb_list = inline_keyb_markup.inline_keyboard
                        inline_keyb_markup = InlineKeyboardMarkup(paginate_keyb_list + delivery_keyb_list)

                    update.message.reply_text(books_layout, reply_markup=inline_keyb_markup)

                else:
                    update.message.reply_text('Sizda hali buyurtmalar mavjud emas !')
                return

            # Biz ijtimoiy tarmoqlarda
            elif re.search(f'{social_nets_btn}$', update.message.text):
                inline_keyb_markup = InlineKeyboard(social_medias_keyboard, user[LANG]).get_markup()
                update.message.reply_photo(PHOTOS_URL + 'kitappuz_photo.jpg', reply_markup=inline_keyb_markup)
                return

            # Biz bilan bo'glanish
            elif re.search(f'{contact_us_btn}$', update.message.text):
                contact_us_text = get_contact_us_text()
                contact_us_text = contact_us_text['text'] if contact_us_text else update.message.text
                update.message.reply_text(contact_us_text)
                return

            else:
                thinking_emoji = '🤔🤔'
                update.message.reply_text(thinking_emoji, quote=True)
                return

    else:
        reply_text = "🔴 Siz ro'yxatdan o'tmagansiz !\nBuning uchun /start ni bosing"
        update.message.reply_text(reply_text)
        return


message_handler = MessageHandler(Filters.text & (~ Filters.command & ~Filters.update.edited_message),
                                 message_handler_callback)
