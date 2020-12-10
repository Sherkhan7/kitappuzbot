from telegram.ext import CallbackQueryHandler, CallbackContext
from telegram import Update, InputMediaPhoto, ParseMode
from telegram.utils.helpers import DefaultValue
from helpers import set_user_data
from languages import LANGS
from config import PHOTOS_URL
from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from globalvariables import *
from DB import get_order_items, update_order_status, get_user
from layouts import get_book_layout
import json
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logger = logging.getLogger()


def inline_keyboards_handler_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    set_user_data(update.effective_user.id, user_data)
    user = user_data['user_data']

    callback_query = update.callback_query
    data = callback_query.data

    print('inline_keyboards_handler_callback', data)

    # with open('jsons/callback_query.json', 'w') as callback_query_file:
    #     callback_query_file.write(callback_query.to_json())

    match_obj = re.search(r'^[rcd]_\d+$', data)
    match_obj_2 = re.search(r'[rcd]_[yn]_\d+$', data)
    new_text = ''

    if match_obj:
        data = match_obj.string.split('_')
        keyboard = choose_keyboard

    elif match_obj_2:
        data = match_obj_2.string.split('_')
        order = get_order_items(data[-1])
        geo = json.loads(order[GEOLOCATION]) if order[GEOLOCATION] else None

        if data[1] == 'n':
            keyboard = orders_keyboard if data[0] == 'r' or data[0] == 'c' else delivery_keyboard
            data = [geo, data[-1]]

        else:
            status = 'delivered' if data[0] == 'd' else 'canceled' if data[0] == 'c' else 'received'
            update_order_status(status, data[-1])
            keyboard = delivery_keyboard if data[0] == 'r' else None

            new_text = callback_query.message.text.split('\n')
            new_text[-1] = f'Status: {status}'
            new_text = '\n'.join(new_text)

            if data[0] == 'r':
                context.bot.send_message(order[USER_TG_ID], 'Buyurtma qabul qilindi',
                                         parse_mode=ParseMode.HTML, reply_to_message_id=order[MESSAGE_ID])
            data = [data[0], data[-1]] if keyboard == choose_keyboard else [geo, data[-1]]

    if new_text:
        if keyboard:
            inline_keyboard = InlineKeyboard(keyboard, user[LANG], data=data).get_keyboard()
        else:
            inline_keyboard = None

        callback_query.edit_message_text(new_text, reply_markup=inline_keyboard, parse_mode=ParseMode.MARKDOWN)
    else:
        inline_keyboard = InlineKeyboard(keyboard, user[LANG], data=data).get_keyboard()
        callback_query.edit_message_reply_markup(inline_keyboard)

    callback_query.answer()

    logger.info('user_data: %s', user_data)


inline_keyboard_handler = CallbackQueryHandler(inline_keyboards_handler_callback)
