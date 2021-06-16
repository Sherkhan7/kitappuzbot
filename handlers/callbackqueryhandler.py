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

    if user[IS_ADMIN]:
        # receive/cancel object for receive/cancel order
        receive_cancel_obj = re.search(r'^[rc]_\d+$', callback_query.data)
        # yes/no object for receive/cancel order
        yes_no_obj = re.search(r'[rc]_[yn]_\d+$', callback_query.data)
        # wanted object for received orders pagination
        wanted_obj = re.search(r'^w_\d+$', callback_query.data)
        # wanted object for history pagination
        history_wanted_obj = re.search(r'^h_w_\d+$', callback_query.data)

        if receive_cancel_obj or yes_no_obj:
            if receive_cancel_obj:
                data = receive_cancel_obj.string.split('_')
                keyboard = yes_no_keyboard
                data = [data[0], data[-1]]

            elif yes_no_obj:
                data = yes_no_obj.string.split('_')
                status = 'canceled' if data[0] == 'c' else 'received'
                answer = data[1]
                order_id = data[-1]

                if answer == 'n':
                    keyboard = orders_keyboard
                    data = order_id

                else:
                    order = get_order(order_id)

                    if order[STATUS] == 'waiting':
                        if status == 'canceled':
                            status_text = 'rad qilindi'
                            client_text = 'Buyurtma rad qilindi'
                            inline_keyb_markup = None
                        else:
                            status_text = 'qabul qilindi'
                            client_text = 'Buyurtma qabul qilindi'

                        if update_order_status(status, order_id):
                            client_text = wrap_tags(client_text) + f' [ 🆔 {order[ID]} ]'

                            if status == 'received':
                                client_text += '\nBuyurtma yetkazilganidan keyin ' \
                                               f'{wrap_tags("Yetkazib berildi")} tugmasini bosing'
                                inline_keyb_markup = InlineKeyboard(delivery_keyboard, user[LANG],
                                                                    order_id).get_markup()

                            # send message to a client
                            context.bot.send_message(order[USER_TG_ID], client_text,
                                                     reply_to_message_id=order[MESSAGE_ID],
                                                     reply_markup=inline_keyb_markup)

                    elif order[STATUS] == 'received':
                        status_text = 'avval qabul qilingan'

                    elif order[STATUS] == 'delivered':
                        status_text = 'avval yetkazilgan'

                    elif order[STATUS] == 'canceled':
                        status_text = 'avval rad qilingan'

                    edit_msg_text = callback_query.message.text_html.split('\n')
                    edit_msg_text[0] = ' '.join(edit_msg_text[0].split()[:2])
                    edit_msg_text[-1] = f'Status: {wrap_tags(status_text)}'
                    edit_msg_text = '\n'.join(edit_msg_text)

            # here `UnboundLocalError: local variable 'edit_msg_text' referenced before assignment` error will be rised
            try:
                callback_query.edit_message_text(edit_msg_text)
                callback_query.answer(f"Buyurtma {status_text} ❕", show_alert=True)

            except UnboundLocalError:
                inline_keyb_markup = InlineKeyboard(keyboard, user[LANG], data=data).get_markup()
                try:
                    callback_query.edit_message_reply_markup(inline_keyb_markup)
                    callback_query.answer()
                except TelegramError:
                    pass

        elif wanted_obj or history_wanted_obj:
            callback_query.answer()
            if history_wanted_obj:
                orders = get_orders_by_status('delivered', 'canceled')
                history = True
                label = '[Tarix]'

            else:
                orders = get_orders_by_status('received')
                history = None
                label = ''

            if orders:
                wanted = int(callback_query.data.split('_')[-1])
                wanted = 1 if wanted > len(orders) else wanted
                order = orders[wanted - 1]
                client = get_user(order[USER_ID])
                if order['with_action']:
                    label += "[🔥MEGA AKSIYA🔥]"
                status = 'yetkazilgan' if order[STATUS] == 'delivered' else 'rad etilgan' \
                    if order[STATUS] == 'canceled' else 'qabul qilingan'
                order_items = get_order_items_book_title(order[ID])
                books_layout = get_books_layout(order, order_items, client, {STATUS: status, 'label': label})
                inline_keyb_markup = InlineKeyboard(paginate_keyboard, user[LANG], [wanted, orders],
                                                    history).get_markup()
                callback_query.edit_message_text(books_layout, reply_markup=inline_keyb_markup)

            else:
                callback_query.edit_message_text("Tarix bo'limiga o'ting !")

        else:
            callback_query.answer()

    else:
        # wanted object for user orders pagination
        wanted_obj = re.search(r'^w_\d+$', callback_query.data)
        # delivered object
        delivered_obj = re.search(r'^d_\d+$', callback_query.data)
        callback_query.answer()

        if wanted_obj:
            wanted = int(wanted_obj.string.split('_')[-1])
            user_orders = get_user_orders(user[ID])
            order = user_orders[wanted - 1]
            order_items = get_order_items_book_title(order[ID])
            label = "[🔥MEGA AKSIYA🔥]" if order['with_action'] else ''
            status = 'qabul qilingan' if order[STATUS] == 'received' else 'rad etilgan' if order[STATUS] == 'canceled' \
                else 'qabul qilish kutilmoqda' if order[STATUS] == 'waiting' else 'yetkazilgan'
            books_layout = get_books_layout(order, order_items, user, {STATUS: status, 'label': label})
            inline_keyb_markup = InlineKeyboard(paginate_keyboard, user[LANG], [wanted, user_orders]).get_markup()

            if order[STATUS] == 'received':
                delivery_keyb = InlineKeyboard(delivery_keyboard, user[LANG], order[ID]).get_markup()
                delivery_keyb_list = delivery_keyb.inline_keyboard
                paginate_keyb_list = inline_keyb_markup.inline_keyboard
                inline_keyb_markup = InlineKeyboardMarkup(paginate_keyb_list + delivery_keyb_list)

            callback_query.edit_message_text(books_layout, reply_markup=inline_keyb_markup)
            return

        elif delivered_obj:
            order_id = delivered_obj.string.split('_')[-1]
            update_order_status('delivered', order_id)

            text = callback_query.message.text_html
            if len(callback_query.message.reply_markup.inline_keyboard) == 1:
                text += f"\nStatus: {wrap_tags('yetkazilgan')}"
                callback_query.edit_message_text(text)

            else:
                inline_keyb_markup = callback_query.message.reply_markup
                del inline_keyb_markup.inline_keyboard[-1]
                callback_query.edit_message_text(text, reply_markup=inline_keyb_markup)


callback_query_handler = CallbackQueryHandler(inline_keyboards_handler_callback)
