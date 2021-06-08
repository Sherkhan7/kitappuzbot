import ujson
import re

from telegram.ext import CallbackQueryHandler, CallbackContext
from telegram import Update, InlineKeyboardMarkup, TelegramError

from DB import *
from globalvariables import *
from helpers import wrap_tags
from layouts import get_books_layout

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *


def inline_keyboards_handler_callback(update: Update, context: CallbackContext):
    # with open('jsons/callback_query.json', 'w') as callback_query_file:
    #     callback_query_file.write(callback_query.to_json())
    user = get_user(update.effective_user.id)
    callback_query = update.callback_query
    data = callback_query.data

    if user[IS_ADMIN]:
        match_obj = re.search(r'^[rc]_\d+$', data)
        match_obj_2 = re.search(r'[rc]_[yn]_\d+$', data)
        match_obj_3 = re.search(r'^w_\d+$', data)
        match_obj_4 = re.search(r'^h_w_\d+$', data)
        new_text = ''

        if match_obj or match_obj_2:

            if match_obj:
                data = match_obj.string.split('_')
                keyboard = yes_no_keyboard

            elif match_obj_2:
                data = match_obj_2.string.split('_')
                order = get_order(data[-1])
                geo = ujson.loads(order[GEOLOCATION]) if order[GEOLOCATION] else None

                if data[1] == 'n':
                    keyboard = orders_keyboard
                    data = [geo, data[-1]]

                elif data[1] == 'y':
                    status = 'canceled' if data[0] == 'c' else 'received'

                    if order[STATUS] == 'waiting':
                        update_result = update_order_status(status, data[-1])
                        status_text = 'rad etilgan' if status == 'canceled' else 'qabul qilingan'

                        if update_result:
                            client_text = 'Buyurtma rad qilindi' if status == 'canceled' else 'Buyurtma qabul qilindi'
                            client_text = wrap_tags(client_text) + f' [ 🆔 {order[ID]} ]'

                            if status == 'received':
                                client_text += '\nBuyurtma yetkazilganidan keyin ' \
                                               f'{wrap_tags("Yetkazib berildi")} tugmasini bosing.\n'
                                inline_keyboard = InlineKeyboard(delivery_keyboard, user[LANG],
                                                                 data=data[-1]).get_keyboard()
                            else:
                                inline_keyboard = None

                            context.bot.send_message(order[USER_TG_ID], client_text,
                                                     reply_to_message_id=order[MESSAGE_ID],
                                                     reply_markup=inline_keyboard)

                    elif order[STATUS] == 'received':
                        status_text = 'buyurtma avval qabul qilingan !'

                    elif order[STATUS] == 'delivered':
                        status_text = 'buyurtma avval yetkazilgan !'

                    elif order[STATUS] == 'canceled':
                        status_text = 'buyurtma avval rad qilingan !'

                    data, keyboard = (geo, geo_keyboard) if geo else (None, None)
                    new_text = callback_query.message.text_html.split('\n')
                    new_text[0] = ' '.join(new_text[0].split()[:2])
                    new_text[-1] = f'Status: {wrap_tags(status_text)}'
                    new_text = '\n'.join(new_text)

            callback_query.answer()

            if new_text:
                if keyboard:
                    inline_keyboard = InlineKeyboard(keyboard, user[LANG], data=data).get_keyboard()
                else:
                    inline_keyboard = None
                callback_query.edit_message_text(new_text, reply_markup=inline_keyboard)

            else:
                inline_keyboard = InlineKeyboard(keyboard, user[LANG], data=data).get_keyboard()
                try:
                    callback_query.edit_message_reply_markup(inline_keyboard)
                except TelegramError:
                    pass

        elif match_obj_3 or match_obj_4:
            if match_obj_4:
                orders = get_orders_by_status(('delivered', 'canceled'))
                history = True
                label = '[Tarix]'

            else:
                orders = get_orders_by_status('received')
                history = None
                label = ''

            if orders:
                wanted = int(data.split('_')[-1])
                order = orders[wanted - 1]
                client = get_user(order[USER_ID])
                if wanted > len(orders):
                    wanted = 1
                if order['with_action']:
                    label += "[🔥MEGA AKSIYA🔥]"
                status = 'yetkazilgan' if order[STATUS] == 'delivered' else 'rad etilgan' \
                    if order[STATUS] == 'canceled' else 'qabul qilingan'
                order_items = get_order_items_book_title(order[ID])
                books_layout = get_books_layout(order, order_items, client, {STATUS: status, 'label': label})
                inline_keyboard = InlineKeyboard(paginate_keyboard, user[LANG], data=[wanted, orders],
                                                 history=history).get_keyboard()
                callback_query.edit_message_text(books_layout, reply_markup=inline_keyboard)

                # if order[GEOLOCATION]:
                #     geo = ujson.loads(order[GEOLOCATION])
                #     inline_keyboard = inline_keyboard.inline_keyboard
                #     keyboard = InlineKeyboard(geo_keyboard, data=geo).get_keyboard().inline_keyboard
                #     inline_keyboard += keyboard
                #     inline_keyboard = InlineKeyboardMarkup(inline_keyboard)

            else:
                text = "Tarix bo'limiga o'ting !"
                callback_query.edit_message_text(text)

        else:
            callback_query.answer()

    else:
        match_obj = re.search(r'^w_\d+$', data)
        match_obj_2 = re.search(r'^d_\d+$', data)
        callback_query.answer()

        if match_obj:
            wanted = int(match_obj.string.split('_')[-1])
            user_orders = get_user_orders(user[ID])
            order = user_orders[wanted - 1]
            order_items = get_order_items_book_title(order[ID])
            label = ''
            if order['with_action']:
                label = "[🔥MEGA AKSIYA🔥]"
            status = 'qabul qilingan' if order[STATUS] == 'received' else 'rad etilgan' \
                if order[STATUS] == 'canceled' else 'qabul qilish kutilmoqda' \
                if order[STATUS] == 'waiting' else 'yetkazilgan'
            books_layout = get_books_layout(order, order_items, user, {STATUS: status, 'label': label})
            inline_keyboard = InlineKeyboard(paginate_keyboard, user[LANG], data=[wanted, user_orders]) \
                .get_keyboard()

            if order[STATUS] == 'received':
                deliv_keyb = InlineKeyboard(delivery_keyboard, user[LANG], data=order[ID]).get_keyboard()
                pag_keyb = inline_keyboard.inline_keyboard
                deliv_keyb = deliv_keyb.inline_keyboard
                inline_keyboard = InlineKeyboardMarkup(pag_keyb + deliv_keyb)

            callback_query.edit_message_text(books_layout, reply_markup=inline_keyboard)
            return

        elif match_obj_2:
            order_id = data.split('_')[-1]
            status = 'delivered'
            update_order_status(status, order_id)

            status = 'yetkazilgan'
            text = callback_query.message.text_html.split('\n')
            if len(callback_query.message.reply_markup.inline_keyboard) == 1:
                text += [
                    f'\nStatus: {wrap_tags(status)}'
                ]
                text = '\n'.join(text)
                callback_query.edit_message_text(text)

            else:
                text[2] = f'Status: {wrap_tags(status)}'
                text = '\n'.join(text)
                inline_keyboard = InlineKeyboardMarkup([callback_query.message.reply_markup.inline_keyboard[0]])
                callback_query.edit_message_text(text, reply_markup=inline_keyboard)


callback_query_handler = CallbackQueryHandler(inline_keyboards_handler_callback)
