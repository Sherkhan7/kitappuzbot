from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackContext, Filters

from globalvariables import *
from DB import insert_data, get_user
from filters import fullname_filter
from helpers import wrap_tags
from languages import LANGS

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *


def do_command(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    command = update.message.text

    if command == '/start' or command == '/menu':
        if user:
            if user[LANG] == LANGS[0]:
                text = "Siz ro'yxatdan o'tgansiz !"
                emoji = "⚠"

            if command == '/menu':
                if user[LANG] == LANGS[0]:
                    text = "Menyu"
                    emoji = "📖"

            menu_keyboard = admin_menu_keyboard if user[IS_ADMIN] else client_menu_keyboard
            reply_keyboard = ReplyKeyboard(menu_keyboard, user[LANG]).get_keyboard()
            update.message.reply_text(f'{emoji} {text}', reply_markup=reply_keyboard)
            return ConversationHandler.END

        else:
            update.message.reply_text('Ism va familyangizni yuboring:')
            user_data[TG_ID] = update.effective_user.id
            user_data[USERNAME] = update.effective_user.username
            user_data[IS_ADMIN] = False
            user_data[LANG] = 'uz'
            return FULLNAME


def fullname_callback(update: Update, context: CallbackContext):
    # with open('jsons/update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user_data = context.user_data
    fullname = fullname_filter(update.message.text)

    if fullname:
        user_data[FULLNAME] = fullname
        insert_data(user_data, 'users')

        if user_data[LANG] == LANGS[0]:
            text = "Tabriklaymiz !\n" \
                   "Siz ro'yxatdan muvofaqqiyatli o'tdingiz\n\n" \
                   "Kitob buyurtma qilishingiz mumkin"

        text = f'🎉🎉🎉 {text}'
        reply_keyboard = ReplyKeyboard(client_menu_keyboard, user_data[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        user_data.clear()
        return ConversationHandler.END

    else:
        if user_data[LANG] == LANGS[0]:
            text = "Ism va familya xato yuborildi !\n" \
                   "Qaytadan quyidagi formatda yuboring"
            example = "Misol: Sherzodbek Esanov yoki Sherzodbek"

        text = f'❗ {text}:\n\nℹ {wrap_tags(example)}'
        update.message.reply_text(text, quote=True)
        return


registration_conversation_handler = ConversationHandler(
    entry_points=[
        CommandHandler(['start', 'menu'], do_command, filters=~Filters.update.edited_message),
    ],
    states={
        FULLNAME: [MessageHandler(Filters.text & (~Filters.update.edited_message), fullname_callback)],
    },
    fallbacks=[],

    persistent=True,

    name='registration_conversation'
)
