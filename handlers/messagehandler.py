from telegram.ext import Filters, MessageHandler, CallbackContext
from telegram import Update
from helpers import set_user_data
from languages import LANGS
from config import PHOTOS_URL
from replykeyboards.replykeyboardtypes import reply_keyboard_types
from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *
from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from globalvariables import *


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
            pass
            # if text == reply_keyboard_types[admin_menu_keyboard][user[LANG]][1]:

            # inline_keyboard = InlineKeyboard(books_keyboard, user[LANG]).get_keyboard()
            # photo = PHOTOS_URL
            #
            # update.message.reply_text('Kitoblar')
            # update.message.reply_photo(photo, reply_markup=inline_keyboard)

            # elif text == reply_keyboard_types[menu_keyboard][user[LANG]][4]:
            #
            #     reply_keyboard = ReplyKeyboard(settings_keyboard, user[LANG]).get_keyboard()
            #     update.message.reply_text(full_text, reply_markup=reply_keyboard)

        else:

            if text == reply_keyboard_types[user_menu_keyboard][user[LANG]][2]:
                # update.message.reply_text('Kitoblar')
                update.message.reply_text()

            elif text == reply_keyboard_types[user_menu_keyboard][user[LANG]][3]:
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
