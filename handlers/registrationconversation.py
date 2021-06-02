import logging

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackContext, Filters

from config import ACTIVE_ADMINS
from DB import insert_data, get_user
from filters import *
from helpers import wrap_tags
from languages import LANGS
from globalvariables import *

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

logger = logging.getLogger()


def do_command(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    command = update.message.text

    if command == '/start' or command == '/menu':
        if user:
            if user[LANG] == LANGS[0]:
                text = "Siz ro'yxatdan o'tgansiz"

            # if user[LANG] == LANGS[1]:
            #     text = "Вы зарегистрированы"
            #
            # if user[LANG] == LANGS[2]:
            #     text = "Сиз рўйхатдан ўтгансиз"

            text = f'⚠ {text} !'

            if command == '/menu':
                if user[LANG] == LANGS[0]:
                    reply_text = "Menyu"

                # if user[LANG] == LANGS[1]:
                #     reply_text = "Меню"
                #
                # if user[LANG] == LANGS[2]:
                #     reply_text = "Меню"

                text = f'📖 {reply_text}'

            menu_keyboard = admin_menu_keyboard if user[IS_ADMIN] else client_menu_keyboard
            reply_keyboard = ReplyKeyboard(menu_keyboard, user[LANG]).get_keyboard()
            update.message.reply_text(text, reply_markup=reply_keyboard)
            state = ConversationHandler.END

        else:
            text = 'Ism va familyangizni yuboring:'
            update.message.reply_text(text)

            user_data[TG_ID] = update.effective_user.id
            user_data[USERNAME] = update.effective_user.username
            user_data[IS_ADMIN] = update.effective_user.id in ACTIVE_ADMINS
            user_data[LANG] = 'uz'
            state = FULLNAME

        # logger.info('user_data: %s', user_data)
        return state


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
                   "Siz ro'yxatdan muvofaqqiyatli o'tdingiz\n\n"

        # if user_data[LANG] == LANGS[1]:
        #     text = "Поздравляем !\n" \
        #            "Вы успешно зарегистрировались\n\n"
        #
        # if user_data[LANG] == LANGS[2]:
        #     text = "Табриклаймиз !\n" \
        #            "Сиз рўйхатдан мувофаққиятли ўтдингиз\n\n"

        if user_data[IS_ADMIN]:
            text += "Buyurtmalarni qabul qilishingiz mumkin"
            menu_keyboard = admin_menu_keyboard

        else:
            text += "Kitob buyurtma qilishingiz mumkin"
            menu_keyboard = client_menu_keyboard

        text = f'\U0001F44F\U0001F44F\U0001F44F {text}'
        reply_keyboard = ReplyKeyboard(menu_keyboard, user_data[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        user_data.clear()
        state = ConversationHandler.END

    else:
        if user_data[LANG] == LANGS[0]:
            text = "Ism va familya xato yuborildi !\n" \
                   "Qaytadan quyidagi formatda yuboring"
            example = "Misol: Sherzodbek Esanov yoki Sherzodbek"

        # if user_data[LANG] == LANGS[1]:
        #     text = 'Имя и фамилия введено неверное !\n' \
        #            'Отправьте еще раз в следующем формате'
        #     example = 'Пример: Шерзод Эсанов'
        #
        # if user_data[LANG] == LANGS[2]:
        #     text = "Исм ва фамиля хато юборилди !\n" \
        #            "Қайтадан қуйидаги форматда юборинг"
        #     example = "Мисол: Шерзод Эсанов"

        text = f'\U000026A0 {text}:\n\n {wrap_tags(example)}'
        update.message.reply_text(text, quote=True)
        state = FULLNAME

    # logger.info('user_data: %s', user_data)
    return state


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
