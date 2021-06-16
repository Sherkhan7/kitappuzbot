from telegram import (
    Update,
    InputMediaPhoto,
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
from DB import *
from handlers.editbooksconversation import (
    edit_contactus_conversation_fallback,
    get_state_text,
    not_back_to_editing_btn_pattern,
    back_to_editing_btn_pattern,
)
from helpers import delete_message_by_message_id
from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardtypes import reply_keyboard_types
from replykeyboards.replykeyboardvariables import *
from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

edit_actions_btn_text = reply_keyboard_types[edit_bot_keyboard]['edit_actions_btn'][f'text_uz']


def get_action_data_dict(user_data):
    return {
        TITLE: user_data[EDIT_ACTION_TITLE],
        PRICE: user_data[EDIT_ACTION_PRICE],
        PHOTO: user_data[EDIT_ACTION_PHOTO][-1].file_id,
        'text': user_data[EDIT_ACTION_TEXT]
    }


def edit_actions_conversation_callback(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    caption = "Tahrirlash uchun aksiyani tanlang tanlang:"
    photo = PHOTOS_URL + 'kitappuz_photo.jpg'

    reply_keyb_markup = ReplyKeyboard(back_keyboard, user[LANG]).get_markup()
    update.message.reply_text(update.message.text, reply_markup=reply_keyb_markup)

    inline_keyb_markup = InlineKeyboard(edit_actions_keyboard, user[LANG], get_all_actions()).get_markup()
    message = update.message.reply_photo(photo, caption=caption, reply_markup=inline_keyb_markup)

    user_data[STATE] = EDIT_ACTIONS
    user_data[MESSAGE_ID] = message.message_id
    return EDIT_ACTIONS


def edit_actions_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if callback_query.data == 'add_action':
        reply_keyb_markup = ReplyKeyboard(back_to_editing_keyboard, user[LANG]).get_markup()
        reply_keyb_markup.keyboard.pop(0)
        callback_query.message.reply_text(get_state_text(EDIT_ACTION_TITLE), reply_markup=reply_keyb_markup)
        try:
            callback_query.delete_message()
        except TelegramError:
            callback_query.edit_message_reply_markup()
        state = EDIT_ACTION_TITLE

    else:
        action_id = callback_query.data.split('_')[-1]
        action = get_action(action_id)
        caption = action['text'] + f"\n\nJami: {action[PRICE]:,} so'm".replace(',', ' ')
        media_photo = InputMediaPhoto(action[PHOTO], caption)
        inline_keyb_markup = InlineKeyboard(edit_action_keyboard, user[LANG]).get_markup()
        try:
            callback_query.edit_message_media(media_photo, reply_markup=inline_keyb_markup)
        except TelegramError:
            pass
        user_data['action_id'] = action_id
        state = EDIT_ACTION

    user_data[STATE] = state
    return state


def edit_action_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if callback_query.data == 'back':
        media_photo = InputMediaPhoto(PHOTOS_URL + 'kitappuz_photo.jpg')
        inline_keyb_markup = InlineKeyboard(edit_actions_keyboard, user[LANG], get_all_actions()).get_markup()
        try:
            callback_query.edit_message_media(media_photo, reply_markup=inline_keyb_markup)
        except TelegramError:
            pass
        del user_data['action_id']
        state = EDIT_ACTIONS

    elif callback_query.data == 'delete_action':
        ask_text = "O'chirishni tasdiqlaysizmi ?"
        inline_keyb_markup = InlineKeyboard(yes_no_keyboard, user[LANG], ['delete', 'action']).get_markup()
        inline_keyb_markup.inline_keyboard.insert(0, [InlineKeyboardButton(ask_text, callback_data='none')])
        callback_query.edit_message_reply_markup(inline_keyb_markup)
        state = YES_NO_CONFIRMATION

    user_data[STATE] = state
    return state


def edit_action_photo_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    if not update.message.photo:
        update.message.reply_text(get_state_text(EDIT_ACTION_PHOTO, True), quote=True)
        return
    update.message.reply_text(get_state_text(EDIT_ACTION_PRICE))
    user_data[EDIT_ACTION_PHOTO] = update.message.photo
    user_data[STATE] = EDIT_ACTION_PRICE
    return EDIT_ACTION_PRICE


def edit_action_title_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    update.message.reply_text(get_state_text(EDIT_ACTION_TEXT))
    user_data[EDIT_ACTION_TITLE] = update.message.text
    user_data[STATE] = EDIT_ACTION_TEXT
    return EDIT_ACTION_TEXT


def edit_action_price_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    action_price = update.message.text.replace(' ', '')
    ask_text = "Aksiyani tasdiqlaysizmi ?"

    if not action_price.isdigit() or int(action_price) > 5000000:
        update.message.reply_text(get_state_text(EDIT_ACTION_PRICE, True), quote=True)
        return

    user_data[EDIT_ACTION_PRICE] = int(action_price)
    inline_keyb_markup = InlineKeyboard(yes_no_keyboard, user[LANG], ['confirm', 'action']).get_markup()
    inline_keyb_markup.inline_keyboard.insert(0, [InlineKeyboardButton(ask_text, callback_data='none')])
    caption = user_data[EDIT_ACTION_TEXT] + f"\n\nJami: {user_data[EDIT_ACTION_PRICE]:,} so'm".replace(',', ' ')
    message = update.message.reply_photo(user_data[EDIT_ACTION_PHOTO][-1].file_id, caption,
                                         reply_markup=inline_keyb_markup)
    user_data[STATE] = YES_NO_CONFIRMATION
    user_data[MESSAGE_ID] = message.message_id
    return YES_NO_CONFIRMATION


def edit_action_text_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    user_data[EDIT_ACTION_TEXT] = update.message.text
    update.message.reply_text(get_state_text(EDIT_ACTION_PHOTO))
    user_data[STATE] = EDIT_ACTION_PHOTO
    return EDIT_ACTION_PHOTO


def yes_no_confirm_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data.split('_')

    if data[0] == 'delete' and data[-1] == 'action':
        if data[1] == 'n':
            inline_keyb_markup = InlineKeyboard(edit_action_keyboard, user[LANG]).get_markup()
            callback_query.edit_message_reply_markup(inline_keyb_markup)
            state = EDIT_ACTION

        elif data[1] == 'y':
            if delete_action(user_data['action_id']) == 'updated':
                callback_query.answer("Aksiya o'chirildi 🙂", show_alert=True)
            caption = "Tahrirlash uchun aksiyani tanlang:"
            photo = PHOTOS_URL + 'kitappuz_photo.jpg'
            media_photo = InputMediaPhoto(photo, caption)
            inline_keyb_markup = InlineKeyboard(edit_actions_keyboard, user[LANG], get_all_actions()).get_markup()

            try:
                callback_query.edit_message_media(media_photo, reply_markup=inline_keyb_markup)
            except TelegramError:
                pass
            state = EDIT_ACTIONS
            if 'action_id' in user_data:
                del user_data['action_id']

        user_data[STATE] = EDIT_BOOKS
        return state

    elif data[0] == 'confirm' and data[-1] == 'action':
        if data[1] == 'y':
            if insert_data(get_action_data_dict(user_data), 'actions'):
                callback_query.answer("Yangi aksiya qo'shildi 😉", show_alert=True)
        else:
            callback_query.answer("🤔 Aksiya tasdiqlanmadi !", show_alert=True)
        return back_to_editing_callback(update, context)


def back_to_editing_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    photo = PHOTOS_URL + 'kitappuz_photo.jpg'
    caption = "Tahrirlash uchun aksiyani tanlang:"
    inline_keyb_markup = InlineKeyboard(edit_actions_keyboard, user[LANG], get_all_actions()).get_markup()
    reply_keyb_markup = ReplyKeyboard(back_keyboard, user[LANG]).get_markup()
    message_obj = update.callback_query.message if update.callback_query else update.message
    state = EDIT_ACTIONS

    message_obj.reply_text('💥 ' + edit_actions_btn_text, reply_markup=reply_keyb_markup)
    # this try except used for send old books' photo like rework.jpg, drive.jpg etc.
    try:
        message = message_obj.reply_photo(photo, caption, reply_markup=inline_keyb_markup)
    except TelegramError:
        pass
    delete_message_by_message_id(context, user)
    user_data.clear()
    user_data[STATE] = state
    user_data[MESSAGE_ID] = message.message_id
    return state


def edit_books_conversation_fallback(update: Update, context: CallbackContext):
    return edit_contactus_conversation_fallback(update, context)


edit_actions_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(f'{edit_actions_btn_text}$'), edit_actions_conversation_callback)],

    states={
        EDIT_ACTIONS: [CallbackQueryHandler(edit_actions_callback, pattern=r'^(edit_action_\d+|add_action)$')],

        EDIT_ACTION: [CallbackQueryHandler(edit_action_callback, pattern=r'^(back|delete_action)$')],

        EDIT_ACTION_PHOTO: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command) | Filters.photo, edit_action_photo_callback)
        ],
        EDIT_ACTION_TITLE: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command), edit_action_title_callback)
        ],
        EDIT_ACTION_PRICE: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command), edit_action_price_callback)
        ],
        EDIT_ACTION_TEXT: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command), edit_action_text_callback)
        ],
        YES_NO_CONFIRMATION: [CallbackQueryHandler(yes_no_confirm_callback,
                                                   pattern=r'^(delete|confirm)_[yn]_(action)$')]
    },

    fallbacks=[
        MessageHandler(Filters.regex(back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                       & (~Filters.command), back_to_editing_callback),
        MessageHandler(Filters.text, edit_books_conversation_fallback),
    ],

    persistent=True,

    name='edit_actions_conversation'
)
