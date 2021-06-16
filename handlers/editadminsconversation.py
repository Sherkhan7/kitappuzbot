from telegram import (
    Update,
    TelegramError,
    InlineKeyboardButton,
)
from telegram.ext import (
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters,
    CallbackQueryHandler
)

from config import *
from globalvariables import *
from layouts import *
from DB import *
from helpers import wrap_tags, delete_message_by_message_id
from handlers.editbooksconversation import (
    edit_contactus_conversation_fallback,
    get_state_text,
    not_back_to_editing_btn_pattern,
    back_to_editing_btn_pattern
)
from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardtypes import reply_keyboard_types
from replykeyboards.replykeyboardvariables import *
from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

edit_admins_btn_text = reply_keyboard_types[edit_bot_keyboard]['edit_admins_btn'][f'text_uz']


def edit_admins_conversation_callback(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = "Tahrirlash uchun adminni tanlang:"

    reply_keyb_markup = ReplyKeyboard(back_keyboard, user[LANG]).get_markup()
    update.message.reply_text(update.message.text, reply_markup=reply_keyb_markup)

    inline_keyb_markup = InlineKeyboard(edit_admins_keyboard, user[LANG], get_all_admins()).get_markup()
    message = update.message.reply_text(text, reply_markup=inline_keyb_markup)

    user_data[STATE] = EDIT_ADMINS
    user_data[MESSAGE_ID] = message.message_id
    return EDIT_ADMINS


def edit_admins_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if callback_query.data == 'add_admin':
        reply_keyb_markup = ReplyKeyboard(back_to_editing_keyboard, user[LANG]).get_markup()
        reply_keyb_markup.keyboard.pop(0)
        callback_query.message.reply_text(get_state_text(USERNAME), reply_markup=reply_keyb_markup)
        try:
            callback_query.delete_message()
        except TelegramError:
            callback_query.edit_message_reply_markup()
        state = USERNAME

    else:
        user_tg_id = callback_query.data.split('_')[-1]
        admin = get_user(user_tg_id)
        inline_keyb_markup = InlineKeyboard(edit_admin_keyboard, user[LANG]).get_markup()
        callback_query.edit_message_text(get_user_info_layout(admin), reply_markup=inline_keyb_markup)
        user_data['admin_tg_id'] = user_tg_id
        state = EDIT_ADMIN

    user_data[STATE] = state
    return state


def edit_admin_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if callback_query.data == 'back':
        edit_msg_text = "Tahrirlash uchun adminni tanlang:"
        inline_keyb_markup = InlineKeyboard(edit_admins_keyboard, user[LANG], get_all_admins()).get_markup()
        callback_query.edit_message_text(edit_msg_text, reply_markup=inline_keyb_markup)
        del user_data['admin_tg_id']
        state = EDIT_ADMINS

    elif callback_query.data == 'delete_admin':
        admin = get_user(user_data['admin_tg_id'])
        ask_text = "O'chirishni tasdiqlaysizmi ?"
        inline_keyb_markup = InlineKeyboard(yes_no_keyboard, user[LANG], ['delete', admin[TG_ID]]).get_markup()
        inline_keyb_markup.inline_keyboard.insert(0, [InlineKeyboardButton(ask_text, callback_data='none')])
        callback_query.edit_message_reply_markup(inline_keyb_markup)
        state = YES_NO_CONFIRMATION

    user_data[STATE] = state
    return state


def username_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    ask_text = "Yangi adminni tasdiqlaysizmi ?"

    username = update.message.text.replace(' ', '')
    username = username[1:] if username.startswith('@') else username
    expecting_admin = get_user_by_username(username)

    if expecting_admin is None:
        update.message.reply_text(get_state_text(USERNAME, True), quote=True)
        return

    inline_keyb_markup = InlineKeyboard(yes_no_keyboard, user[LANG], ['makeadmin', expecting_admin[TG_ID]]).get_markup()
    inline_keyb_markup.inline_keyboard.insert(0, [InlineKeyboardButton(ask_text, callback_data='none')])

    layout = get_user_info_layout(expecting_admin)
    message = update.message.reply_text(layout, reply_markup=inline_keyb_markup)

    user_data[STATE] = YES_NO_CONFIRMATION
    user_data[MESSAGE_ID] = message.message_id
    return YES_NO_CONFIRMATION


def yes_no_confirm_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data.split('_')
    action = data[0]
    answer = data[1]
    admin_tg_id = data[-1]
    _admin = get_user(admin_tg_id)

    if answer == 'y':
        if _admin[TG_ID] == user[TG_ID] and action == 'delete':
            callback_query.answer("😕 Siz o'zingizni adminlikdan o'chira olmaysiz !", show_alert=True)
            return
        is_admin = True if action == 'makeadmin' else False
        if update_user_isadmin(is_admin, admin_tg_id) != 'updated':
            callback_query.answer("⚠ Foydalanuvchi avval adminlikka tayinlangan !", show_alert=True)
            return

        if action == 'makeadmin':
            opportunity_text = f"- Yangi buyurmalarni ko'rish/qabul qilish/bekor qilish\n" \
                               f"- Qabul qilingan buyurmalarni ko'rish\n" \
                               f"- Barcha foydalanuvchilarga xabar yuborish\n" \
                               f"- Bot ni tahrirlash\n" \
                               f"- Tarix ni ko'rish\n" \
                               f"- Bazani yuklash"
            text = f'Hurmatli {wrap_tags(_admin[FULLNAME])} ❕\n' \
                   f'siz {wrap_tags(user[FULLNAME])} tomonidan @{BOT_USERNAME} ga ' \
                   f'{wrap_tags("adminlikka tayinlandingiz !")} 😃\n\n' \
                   f'🤖 /menu yoki /start kommandasi menga yuboring !\n\n' \
                   f'Endi siz quyidagilarni bajara olasiz:\n{wrap_tags(opportunity_text)}'
            alert_text = f"Foydalanuvchi {_admin[FULLNAME]} adminlikka muvaffaqiyatli tayinlandi 😉"

        else:
            text = f"Hurmatli {wrap_tags(_admin[FULLNAME])} ❕\n" \
                   f"siz {wrap_tags(user[FULLNAME])} tomonidan @{BOT_USERNAME} ga " \
                   f"{wrap_tags('adminlikdan olib tashlandingiz !')} 😬\n\n" \
                   f"🤖 /menu yoki /start kommandasi menga yuboring !"
            alert_text = f"Foydalanuvchi {_admin[FULLNAME]} adminlikdan muvaffaqiyatli olib tashlandi 🙂"

        # send message to the user (new admin or deleted admin)
        try:
            context.bot.send_message(admin_tg_id, text)
        except TelegramError:
            alert_text += "\n⚠ Ammo bu haqda foydalanuvchini xabardor qiling !"

        callback_query.answer(alert_text, show_alert=True)
        return back_to_editing_callback(update, context)

    elif answer == 'n':
        if action == 'makeadmin':
            callback_query.answer('‼ Admin tasdiqlanmadi ! 🤔', show_alert=True)
            return back_to_editing_callback(update, context)
        else:
            inline_keyb_markup = InlineKeyboard(edit_admin_keyboard, user[LANG]).get_markup()
            callback_query.edit_message_text(get_user_info_layout(_admin), reply_markup=inline_keyb_markup)
            user_data[STATE] = EDIT_ADMIN
            return EDIT_ADMIN


def back_to_editing_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    inline_keyb_markup = InlineKeyboard(edit_admins_keyboard, user[LANG], get_all_admins()).get_markup()
    message_obj = update.callback_query.message if update.callback_query else update.message

    reply_keyb_markup = ReplyKeyboard(back_keyboard, user[LANG]).get_markup()
    message_obj.reply_text('👥 ' + edit_admins_btn_text, reply_markup=reply_keyb_markup)

    message = message_obj.reply_text('Tahrirlash uchun adminni tanlang:', reply_markup=inline_keyb_markup)
    delete_message_by_message_id(context, user)
    user_data.clear()
    user_data[STATE] = EDIT_ADMINS
    user_data[MESSAGE_ID] = message.message_id
    return EDIT_ADMINS


def edit_admins_conversation_fallback(update: Update, context: CallbackContext):
    return edit_contactus_conversation_fallback(update, context)


edit_admins_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(f'{edit_admins_btn_text}$'), edit_admins_conversation_callback)],

    states={
        EDIT_ADMINS: [CallbackQueryHandler(edit_admins_callback, pattern=r'^(edit_admin_\d+|add_admin)$')],

        EDIT_ADMIN: [CallbackQueryHandler(edit_admin_callback, pattern=r'^(back|delete_admin)$')],

        USERNAME: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command), username_callback),
        ],
        YES_NO_CONFIRMATION: [CallbackQueryHandler(yes_no_confirm_callback, pattern=r'^(makeadmin|delete)_[yn]_\d+$')]
    },

    fallbacks=[
        MessageHandler(Filters.regex(back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                       & (~Filters.command), back_to_editing_callback),
        MessageHandler(Filters.text & (~Filters.update.edited_message), edit_admins_conversation_fallback),
    ],

    persistent=True,

    name='edit_admins_conversation'
)
