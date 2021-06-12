import re

from telegram import Update, InlineKeyboardButton
from telegram.ext import (
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters,
    CallbackQueryHandler
)

from globalvariables import *
from DB import get_user, update_contact_us_text
from helpers import delete_message_by_message_id
from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardtypes import reply_keyboard_types
from replykeyboards.replykeyboardvariables import *
from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

contact_us_btn_text = reply_keyboard_types[edit_bot_keyboard]['edit_contact_us_btn'][f'text_uz']
back_btn_text = reply_keyboard_types[back_keyboard]['back_btn'][f'text_uz']
not_pattern = f"^(.(?!({back_btn_text})))*$"


def end_conversation(update: Update, context: CallbackContext, user, text, keyboard):
    reply_keyboard = ReplyKeyboard(keyboard, user[LANG]).get_keyboard()
    delete_message_by_message_id(context, user)

    if update.callback_query:
        update.callback_query.message.reply_text(text, reply_markup=reply_keyboard)
    else:
        update.message.reply_text(text, reply_markup=reply_keyboard)

    context.user_data.clear()
    return ConversationHandler.END


def edit_contactus_conversation_callback(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    reply_keyboard = ReplyKeyboard(back_keyboard, user[LANG]).get_keyboard()
    update.message.reply_text("Yangi tekstni kiriting", reply_markup=reply_keyboard)

    user_data[STATE] = EDIT_CONTACTUS_TEXT
    return EDIT_CONTACTUS_TEXT


def edit_cantactus_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    back_obj = re.search(f"({back_btn_text})$", update.message.text)
    if not back_obj:
        user = get_user(update.effective_user.id)
        user_data = context.user_data
        ask_text = "Yangi tekstni tastiqlaysizmi ?"
        inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG], data=['edit', 'contactus']).get_keyboard()
        inline_keyboard.inline_keyboard.insert(0, [InlineKeyboardButton(ask_text, callback_data='none')])
        message = update.message.reply_text(update.message.text_html, reply_markup=inline_keyboard)

        user_data[EDIT_CONTACTUS_TEXT] = update.message.text_html
        user_data[STATE] = CONTACTUS_TEXT_CONFIRMATION
        user_data[MESSAGE_ID] = message.message_id
        return CONTACTUS_TEXT_CONFIRMATION
    emoji = reply_keyboard_types[admin_menu_keyboard]['edit_bot_btn']['emoji']
    text = reply_keyboard_types[admin_menu_keyboard]['edit_bot_btn'][f'text_uz']
    text = f'{emoji} {text}'
    keyboard = edit_bot_keyboard
    return end_conversation(update, context, user, text, keyboard)


def confirm_contactus_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if callback_query.data != 'none':
        if callback_query.data == 'edit_y_contactus':
            alert_text = "Tekst yangilanmadi 😐"
            if update_contact_us_text(user_data[EDIT_CONTACTUS_TEXT]) == 'updated':
                alert_text = "Tekst yangilandi 😃"
            callback_query.answer(alert_text, show_alert=True)

        emoji = reply_keyboard_types[admin_menu_keyboard]['edit_bot_btn']['emoji']
        text = reply_keyboard_types[admin_menu_keyboard]['edit_bot_btn'][f'text_uz']
        text = f'{emoji} {text}'
        return end_conversation(update, context, user, text, edit_bot_keyboard)
    callback_query.answer()


def edit_contactus_conversation_fallback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    back_obj = re.search(f"({back_btn_text})$", update.message.text)

    if back_obj or update.message.text == '/cancel' or update.message.text == '/start' \
            or update.message.text == '/menu':

        if back_obj or update.message.text == '/cancel':
            emoji = reply_keyboard_types[admin_menu_keyboard]['edit_bot_btn']['emoji']
            text = reply_keyboard_types[admin_menu_keyboard]['edit_bot_btn'][f'text_uz']
            text = f'{emoji} {text}'
            keyboard = edit_bot_keyboard
        elif update.message.text == '/start' or update.message.text == '/menu':
            text = "📖 Menyu"
            keyboard = admin_menu_keyboard
        return end_conversation(update, context, user, text, keyboard)


edit_contactus_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(f'{contact_us_btn_text}$'), edit_contactus_conversation_callback)],

    states={
        EDIT_CONTACTUS_TEXT: [MessageHandler(Filters.text & (~Filters.update.edited_message) & (~Filters.command),
                                             edit_cantactus_callback)],

        CONTACTUS_TEXT_CONFIRMATION: [CallbackQueryHandler(confirm_contactus_callback,
                                                           pattern=r'^edit_[yn]_contactus|none$')]
    },
    fallbacks=[
        MessageHandler(Filters.text, edit_contactus_conversation_fallback),
    ],

    persistent=True,

    name='edit_contactus_conversation'
)
