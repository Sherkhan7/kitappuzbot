import re
from datetime import datetime

from telegram import (
    Update,
    InputMediaPhoto,
    TelegramError,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters,
    CallbackQueryHandler
)
from validators import url, ValidationFailure

from config import *
from globalvariables import *
from layouts import *
from DB import *
from helpers import wrap_tags, delete_message_by_message_id
from handlers.editcontacusconversation import edit_contactus_conversation_fallback
from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardtypes import reply_keyboard_types
from replykeyboards.replykeyboardvariables import *
from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardtypes import inline_keyboard_types
from inlinekeyboards.inlinekeyboardvariables import *

edit_books_btn_text = reply_keyboard_types[edit_bot_keyboard]['edit_books_btn'][f'text_uz']
back_btn_text = reply_keyboard_types[back_keyboard]['back_btn'][f'text_uz']
back_to_editing_btn_text = reply_keyboard_types[back_to_editing_keyboard]['back_to_editing_btn'][f'text_uz']
next_btn_text = reply_keyboard_types[back_to_editing_keyboard]['next_btn'][f'text_uz']

not_back_btn_pattern = f"^(.(?!({back_btn_text})))*$"
not_back_to_editing_btn_pattern = f"^(.(?!({back_to_editing_btn_text})))*$"
next_btn_pattern = f'^{next_btn_text}'


def get_state_text(state, is_error=False):
    if state == EDIT_BOOK_TITLE:
        text = 'Kitob nomini kiriting:'

    elif state == EDIT_BOOK_LANG:
        text = "Kitob qaysi tilda yozilganligini kiriting :\n\nℹ Misol: O'zbekcha"

    elif state == EDIT_BOOK_TRANSLATOR:
        text = "Kitob tarjimon(lar)ini kiriting :\n\nℹ Misol: Sherzodbek Esanov"

    elif state == EDIT_BOOK_COVER:
        text = "Kitob muqovasi turini kiriting :\n\nℹ Misol: Qattik yoki yumshoq"

    elif state == EDIT_BOOK_PHOTO:
        text = "Kitob uchun rasm yuboring:\n\nℹ Rasmni siqilgan formatda yuboring"
        if is_error:
            text = '⚠ Kechirasiz, rasmni siqilgan formatda yuboring !'

    elif state == EDIT_BOOK_PRICE:
        text = "Kitob narxini kiriting (raqamlar bilan):\n\nℹ Misol: 200 000"
        if is_error:
            text = "⚠ Narxni raqamlar bilan kiriting !\n\nℹ Maksimum: 1 000 000 so'm"

    elif state == EDIT_BOOK_URL:
        text = "Kitob haqida URL(link) ni kiriting :\n\nℹ Misol: https://telegra.ph/Rework-12-08"
        if is_error:
            text = "❗ Bunday URL(link) mavjud emas !\n" \
                   "URL(link) ni quyidagi formatda kiriting:\n\nℹ Misol: https://telegra.ph/Rework-12-08"

    elif state == EDIT_BOOK_AMOUT:
        text = "Kitob hajmini kiriting (raqamlar bilan) :\n\nℹ Misol: 256"
        if is_error:
            text = "⚠ Kitob hajmini raqamlar bilan kiriting !\n\nℹ Maksimum: 1 000 bet"

    elif state == EDIT_BOOK_YEAR:
        text = "Kitob nashrdan chiqqan yilni kiriting (raqamlar bilan) :\n\nℹ Misol: 2000"
        if is_error:
            text = f"⚠ Kitob nashrdan chiqqan yilni raqamlar bilan kiriting !\n\nℹ Maksimum: {datetime.now().year} yil"

    elif state == EDIT_BOOK_AUTHOR:
        text = "Kitob muallif(lar)ini kiriting :\n\nℹ Misol: <b>Robert Kiyosaki</b>"
    return text


def get_book_data_dict(user_data):
    return {
        TITLE: user_data[EDIT_BOOK_TITLE],
        PRICE: user_data[EDIT_BOOK_PRICE],
        PHOTO: user_data[EDIT_BOOK_PHOTO][-1].file_id,
        YEAR: user_data[EDIT_BOOK_YEAR] if EDIT_BOOK_YEAR in user_data else None,
        AUTHOR: user_data[EDIT_BOOK_AUTHOR] if EDIT_BOOK_AUTHOR in user_data else None,
        AMOUNT: user_data[EDIT_BOOK_AMOUT] if EDIT_BOOK_AMOUT in user_data else None,
        LANG: user_data[EDIT_BOOK_LANG] if EDIT_BOOK_LANG in user_data else None,
        TRANSLATOR: user_data[EDIT_BOOK_TRANSLATOR] if EDIT_BOOK_TRANSLATOR in user_data else None,
        COVER_TYPE: user_data[EDIT_BOOK_COVER] if EDIT_BOOK_COVER in user_data else None,
    }


def return_edit_book_callback(update, user, user_data):
    if user_data[STATE] == EDIT_BOOK_PHOTO:
        text = 'Kitob rasmi tahrirlandi'
    elif user_data[STATE] == EDIT_BOOK_TITLE:
        text = 'Kitob nomi tahrirlandi'
    elif user_data[STATE] == EDIT_BOOK_PRICE:
        text = 'Kitob narxi tahrirlandi'
    elif user_data[STATE] == EDIT_BOOK_AUTHOR:
        text = 'Kitob muallif(lar)i tahrirlandi'
    elif user_data[STATE] == EDIT_BOOK_LANG:
        text = 'Kitob tili tahrirlandi'
    elif user_data[STATE] == EDIT_BOOK_TRANSLATOR:
        text = 'Kitob tarjimon(lar)i tahrirlandi'
    elif user_data[STATE] == EDIT_BOOK_COVER:
        text = 'Kitob muqovasi tahrirlandi'
    elif user_data[STATE] == EDIT_BOOK_URL:
        text = 'Kitob URL(link)i tahrirlandi'
    elif user_data[STATE] == EDIT_BOOK_AMOUT:
        text = 'Kitob hajmi tahrirlandi'
    elif user_data[STATE] == EDIT_BOOK_YEAR:
        text = 'Kitob yili tahrirlandi'

    book = get_book(user_data['book_id'])
    caption = get_book_layout(book, user[LANG])
    inline_keyboard = InlineKeyboard(edit_book_keyboard, user[LANG], data=book).get_keyboard()
    # this try except used for send old books' photo like rework.jpg, drive.jpg etc.
    try:
        message = update.message.reply_photo(book[PHOTO], caption, reply_markup=inline_keyboard)
    except TelegramError:
        message = update.message.reply_photo(PHOTOS_URL + book[PHOTO], caption, reply_markup=inline_keyboard)
    reply_keyboard = ReplyKeyboard(back_keyboard, user[LANG]).get_keyboard()
    update.message.reply_text(text + ' 😉', reply_markup=reply_keyboard)

    user_data[MESSAGE_ID] = message.message_id
    user_data[STATE] = EDIT_BOOK
    return EDIT_BOOK


def edit_books_conversation_callback(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    caption = "Tahrirlash uchun kitobni tanlang:"
    photo = PHOTOS_URL + 'kitappuz_photo.jpg'

    reply_keyboard = ReplyKeyboard(back_keyboard, user[LANG]).get_keyboard()
    update.message.reply_text(update.message.text, reply_markup=reply_keyboard)

    inline_keyboard = InlineKeyboard(edit_books_keyboard, user[LANG], data=get_all_books()).get_keyboard()
    message = update.message.reply_photo(photo, caption=caption, reply_markup=inline_keyboard)

    user_data[STATE] = EDIT_BOOKS
    user_data[MESSAGE_ID] = message.message_id
    return EDIT_BOOKS


def edit_books_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if callback_query.data == 'add_book':
        reply_keyboard = ReplyKeyboard(back_to_editing_keyboard, user[LANG]).get_keyboard()
        reply_keyboard.keyboard.pop(0)
        callback_query.message.reply_text(get_state_text(EDIT_BOOK_TITLE), reply_markup=reply_keyboard)
        try:
            callback_query.delete_message()
        except TelegramError:
            callback_query.edit_message_reply_markup()
        user_data[STATE] = EDIT_BOOK_TITLE
        return EDIT_BOOK_TITLE
    else:
        book_id = callback_query.data.split('_')[-1]
        book = get_book(book_id)
        caption = get_book_layout(book, user[LANG])
        media_photo = InputMediaPhoto(book[PHOTO], caption=caption)
        inline_keyboard = InlineKeyboard(edit_book_keyboard, user[LANG], data=book).get_keyboard()
        try:
            callback_query.edit_message_media(media_photo, reply_markup=inline_keyboard)
        except TelegramError:
            media_photo = InputMediaPhoto(PHOTOS_URL + book[PHOTO], caption)
            callback_query.edit_message_media(media_photo, reply_markup=inline_keyboard)
        user_data['book_id'] = book_id
        user_data[STATE] = EDIT_BOOK
        return EDIT_BOOK


def edit_book_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if callback_query.data == 'back':
        media_photo = InputMediaPhoto(PHOTOS_URL + 'kitappuz_photo.jpg')
        inline_keyboard = InlineKeyboard(edit_books_keyboard, user[LANG], data=get_all_books()).get_keyboard()
        try:
            callback_query.edit_message_media(media_photo, reply_markup=inline_keyboard)
        except TelegramError:
            pass
        del user_data['book_id']
        state = EDIT_BOOKS

    elif callback_query.data == 'delete_book':
        book = get_book(user_data['book_id'])
        ask_text = "O'chirishni tasdiqlaysizmi ?"
        inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG], data=['delete', 'book']).get_keyboard()
        inline_keyboard.inline_keyboard.insert(0, [InlineKeyboardButton(ask_text, callback_data='none')])

        if book['description_url']:
            emoji = inline_keyboard_types[book_keyboard]['about_book_btn']['emoji']
            inline_keyboard.inline_keyboard.insert(0, [
                InlineKeyboardButton(f'{emoji} {inline_keyboard_types[book_keyboard]["about_book_btn"]["text_uz"]}',
                                     url=book['description_url'])
            ])
        try:
            callback_query.edit_message_reply_markup(inline_keyboard)
        except TelegramError:
            pass
        state = YES_NO_CONFIRMATION

    else:
        if callback_query.data == 'edit_photo':
            state = EDIT_BOOK_PHOTO

        elif callback_query.data == 'edit_title':
            state = EDIT_BOOK_TITLE

        elif callback_query.data == 'edit_author':
            state = EDIT_BOOK_AUTHOR

        elif callback_query.data == 'edit_amount':
            state = EDIT_BOOK_AMOUT

        elif callback_query.data == 'edit_lang':
            state = EDIT_BOOK_LANG

        elif callback_query.data == 'edit_translator':
            state = EDIT_BOOK_TRANSLATOR

        elif callback_query.data == 'edit_url':
            state = EDIT_BOOK_URL

        elif callback_query.data == 'edit_year':
            state = EDIT_BOOK_YEAR

        elif callback_query.data == 'edit_price':
            state = EDIT_BOOK_PRICE

        elif callback_query.data == 'edit_cover':
            state = EDIT_BOOK_COVER
        try:
            callback_query.delete_message()
        except TelegramError:
            callback_query.edit_message_reply_markup()
        reply_keyboard = ReplyKeyboard(back_to_editing_keyboard, user[LANG]).get_keyboard()
        reply_keyboard.keyboard.pop(0)
        callback_query.message.reply_text(get_state_text(state), reply_markup=reply_keyboard)

    user_data[STATE] = state
    return state


def edit_book_photo_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    if not update.message.photo:
        update.message.reply_text(get_state_text(EDIT_BOOK_PHOTO, True), quote=True)
        return

    if 'book_id' in user_data:
        update_book_photo(update.message.photo[-1].file_id, user_data['book_id'])
        return return_edit_book_callback(update, user, user_data)
    update.message.reply_text(get_state_text(EDIT_BOOK_PRICE))
    user_data[EDIT_BOOK_PHOTO] = update.message.photo
    user_data[STATE] = EDIT_BOOK_PRICE
    return EDIT_BOOK_PRICE


def edit_book_title_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    if 'book_id' in user_data:
        update_book_title(update.message.text, user_data['book_id'])
        return return_edit_book_callback(update, user, user_data)
    update.message.reply_text(get_state_text(EDIT_BOOK_PHOTO))
    user_data[EDIT_BOOK_TITLE] = update.message.text
    user_data[STATE] = EDIT_BOOK_PHOTO
    return EDIT_BOOK_PHOTO


def edit_book_price_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    book_price = update.message.text.replace(' ', '')
    text = "Kitob haqidagi boshqa ma'lumotlarni ham kiritasizmi ?\n\n" \
           f"ℹ Misol: {wrap_tags('Muallif(lar), tarjimon, yil, muqova va hokozolar')}"

    if not book_price.isdigit() or int(book_price) > 1000000:
        update.message.reply_text(get_state_text(EDIT_BOOK_PRICE, True), quote=True)
        return

    if 'book_id' in user_data:
        update_book_price(int(book_price), user_data['book_id'])
        return return_edit_book_callback(update, user, user_data)
    user_data[EDIT_BOOK_PRICE] = int(book_price)
    inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG], data=['continue', 'adding']).get_keyboard()
    message = update.message.reply_text(text, reply_markup=inline_keyboard)
    user_data[STATE] = YES_NO_CONFIRMATION
    user_data[MESSAGE_ID] = message.message_id
    return YES_NO_CONFIRMATION


def edit_book_author_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    next_obj = re.search(next_btn_text, update.message.text)

    if 'book_id' in user_data:
        update_book_author(update.message.text, user_data['book_id'])
        return return_edit_book_callback(update, user, user_data)

    if not next_obj:
        user_data[EDIT_BOOK_AUTHOR] = update.message.text
    update.message.reply_text(get_state_text(EDIT_BOOK_LANG))
    user_data[STATE] = EDIT_BOOK_LANG
    return EDIT_BOOK_LANG


def edit_book_lang_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    next_obj = re.search(next_btn_text, update.message.text)

    if 'book_id' in user_data:
        update_book_lang(update.message.text, user_data['book_id'])
        return return_edit_book_callback(update, user, user_data)

    if not next_obj:
        user_data[EDIT_BOOK_LANG] = update.message.text
    update.message.reply_text(get_state_text(EDIT_BOOK_TRANSLATOR))
    user_data[STATE] = EDIT_BOOK_TRANSLATOR
    return EDIT_BOOK_TRANSLATOR


def edit_book_translator_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    next_obj = re.search(next_btn_text, update.message.text)

    if 'book_id' in user_data:
        update_book_translator(update.message.text, user_data['book_id'])
        return return_edit_book_callback(update, user, user_data)

    if not next_obj:
        user_data[EDIT_BOOK_TRANSLATOR] = update.message.text
    update.message.reply_text(get_state_text(EDIT_BOOK_COVER))
    user_data[STATE] = EDIT_BOOK_COVER
    return EDIT_BOOK_COVER


def edit_book_cover_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    next_obj = re.search(next_btn_text, update.message.text)

    if 'book_id' in user_data:
        update_book_cover(update.message.text, user_data['book_id'])
        return return_edit_book_callback(update, user, user_data)

    if not next_obj:
        user_data[EDIT_BOOK_COVER] = update.message.text
    update.message.reply_text(get_state_text(EDIT_BOOK_URL))
    user_data[STATE] = EDIT_BOOK_URL
    return EDIT_BOOK_URL


def edit_book_url_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    next_obj = re.search(next_btn_text, update.message.text)

    if 'book_id' in user_data:
        # Here validators.url(update.message.text) just retuns validators.ValidationFailure not throwing it
        # link: https://github.com/kvesteri/validators/issues/139
        if isinstance(url(update.message.text), ValidationFailure):
            update.message.reply_text(get_state_text(EDIT_BOOK_URL, True), quote=True)
            return
        update_book_url(update.message.text, user_data['book_id'])
        return return_edit_book_callback(update, user, user_data)

    if not next_obj:
        # Here validators.url(update.message.text) just retuns validators.ValidationFailure not throwing it
        # link: https://github.com/kvesteri/validators/issues/139
        if isinstance(url(update.message.text), ValidationFailure):
            update.message.reply_text(get_state_text(EDIT_BOOK_URL, True), quote=True)
            return
        user_data[EDIT_BOOK_URL] = update.message.text
    update.message.reply_text(get_state_text(EDIT_BOOK_AMOUT))
    user_data[STATE] = EDIT_BOOK_AMOUT
    return EDIT_BOOK_AMOUT


def edit_book_amout_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    next_obj = re.search(next_btn_text, update.message.text)

    if 'book_id' in user_data:
        book_amout = update.message.text.replace(' ', '')
        if not book_amout.isdigit() or int(book_amout) > 10000:
            update.message.reply_text(get_state_text(EDIT_BOOK_AMOUT, True), quote=True)
            return
        update_book_amount(int(book_amout), user_data['book_id'])
        return return_edit_book_callback(update, user, user_data)

    if not next_obj:
        book_amout = update.message.text.replace(' ', '')
        if not book_amout.isdigit() or int(book_amout) > 1000:
            update.message.reply_text(get_state_text(EDIT_BOOK_AMOUT, True), quote=True)
            return
        user_data[EDIT_BOOK_AMOUT] = int(book_amout)
    reply_keyboard = ReplyKeyboard(back_to_editing_keyboard, user[LANG]).get_keyboard()
    reply_keyboard.keyboard.pop(0)
    update.message.reply_text(get_state_text(EDIT_BOOK_YEAR), reply_markup=reply_keyboard)

    user_data[STATE] = EDIT_BOOK_YEAR
    return EDIT_BOOK_YEAR


def edit_book_year_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    ask_text = "Yangi kitobni tasdiqlaysizmi ?"
    next_obj = re.search(next_btn_text, update.message.text)

    if 'book_id' in user_data:
        book_year = update.message.text.replace(' ', '')
        if not book_year.isdigit() or len(book_year) != 4 or int(book_year) > datetime.now().year:
            update.message.reply_text(get_state_text(EDIT_BOOK_YEAR, True), quote=True)
            return
        update_book_year(book_year, user_data['book_id'])
        return return_edit_book_callback(update, user, user_data)

    if not next_obj:
        book_year = update.message.text.replace(' ', '')
        if not book_year.isdigit() or len(book_year) != 4 or int(book_year) > datetime.now().year:
            update.message.reply_text(get_state_text(EDIT_BOOK_YEAR, True), quote=True)
            return
        user_data[EDIT_BOOK_YEAR] = book_year
    update.message.reply_text("✅ Kitobni tasdiqlash", reply_markup=ReplyKeyboardRemove())
    inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG], data=['confirm', 'book']).get_keyboard()
    inline_keyboard.inline_keyboard.insert(0, [InlineKeyboardButton(ask_text, callback_data='none')])

    if EDIT_BOOK_URL in user_data:
        inline_keyboard.inline_keyboard.insert(0, [
            InlineKeyboardButton("🔗 Kitob haqida", url=user_data[EDIT_BOOK_URL])])
    layout = get_book_layout(get_book_data_dict(user_data), user[LANG])
    message = update.message.reply_photo(user_data[EDIT_BOOK_PHOTO][-1].file_id, layout,
                                         reply_markup=inline_keyboard)
    user_data[STATE] = YES_NO_CONFIRMATION
    user_data[MESSAGE_ID] = message.message_id
    return YES_NO_CONFIRMATION


def yes_no_confirm_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data.split('_')

    if data[0] == 'delete' and data[-1] == 'book':
        if data[1] == 'n':
            book = get_book(user_data['book_id'])
            inline_keyboard = InlineKeyboard(edit_book_keyboard, user[LANG], data=book).get_keyboard()
            try:
                callback_query.edit_message_reply_markup(inline_keyboard)
            except TelegramError:
                pass
            state = EDIT_BOOK

        elif data[1] == 'y':
            if delete_book(user_data['book_id']) == 'updated':
                callback_query.answer("Kitob o'chirildi 🙂", show_alert=True)
            caption = "Tahrirlash uchun kitobni tanlang:"
            photo = PHOTOS_URL + 'kitappuz_photo.jpg'
            media_photo = InputMediaPhoto(photo, caption)
            inline_keyboard = InlineKeyboard(edit_books_keyboard, user[LANG], data=get_all_books()).get_keyboard()
            try:
                callback_query.edit_message_media(media_photo, reply_markup=inline_keyboard)
            except TelegramError:
                pass
            state = EDIT_BOOKS
            if 'book_id' in user_data:
                del user_data['book_id']
        user_data[STATE] = EDIT_BOOKS
        return state

    elif data[0] == 'continue' and data[-1] == 'adding':
        if data[1] == 'n':
            try:
                callback_query.delete_message()
            except TelegramError:
                callback_query.edit_message_reply_markup()
            ask_text = "Yangi kitobni tasdiqlaysizmi ?"
            inline_keyboard = InlineKeyboard(yes_no_keyboard, user[LANG], data=['confirm', 'book']).get_keyboard()
            inline_keyboard.inline_keyboard.insert(0, [InlineKeyboardButton(ask_text, callback_data='none')])

            layout = get_book_layout(get_book_data_dict(user_data), user[LANG])
            message = callback_query.message.reply_photo(user_data[EDIT_BOOK_PHOTO][-1].file_id, caption=layout,
                                                         reply_markup=inline_keyboard)
            user_data[MESSAGE_ID] = message.message_id
            return

        elif data[1] == 'y':
            reply_keyboard = ReplyKeyboard(back_to_editing_keyboard, user[LANG]).get_keyboard()
            callback_query.message.reply_text(get_state_text(EDIT_BOOK_AUTHOR), reply_markup=reply_keyboard)
            try:
                callback_query.delete_message()
            except TelegramError:
                callback_query.edit_message_reply_markup()
            user_data[STATE] = EDIT_BOOK_AUTHOR
            return EDIT_BOOK_AUTHOR

    elif data[0] == 'confirm' and data[-1] == 'book':
        if data[1] == 'y':
            caption = "Tahrirlash uchun kitobni tanlang:"
            photo = PHOTOS_URL + 'kitappuz_photo.jpg'

            if insert_data(get_book_data_dict(user_data), 'books'):
                callback_query.answer("Yangi kitob qo'shildi 😉", show_alert=True)
                reply_keyboard = ReplyKeyboard(back_keyboard, user[LANG]).get_keyboard()
                callback_query.message.reply_text('📚 ' + edit_books_btn_text, reply_markup=reply_keyboard)

                inline_keyboard = InlineKeyboard(edit_books_keyboard, user[LANG], data=get_all_books()).get_keyboard()
                message = callback_query.message.reply_photo(photo, caption=caption, reply_markup=inline_keyboard)
                try:
                    callback_query.delete_message()
                except TelegramError:
                    callback_query.edit_message_reply_markup()
                user_data.clear()
                user_data[STATE] = EDIT_BOOKS
                user_data[MESSAGE_ID] = message.message_id
                return EDIT_BOOKS

        if data[1] == 'n':
            caption = "Tahrirlash uchun kitobni tanlang:"
            photo = PHOTOS_URL + 'kitappuz_photo.jpg'
            media_photo = InputMediaPhoto(photo, caption)
            inline_keyboard = InlineKeyboard(edit_books_keyboard, user[LANG], data=get_all_books()).get_keyboard()
            callback_query.edit_message_media(media_photo, reply_markup=inline_keyboard)
            callback_query.answer('Kitob tasdiqlanmadi 🙂', show_alert=True)

            reply_keyboard = ReplyKeyboard(back_keyboard, user[LANG]).get_keyboard()
            callback_query.message.reply_text('📚 ' + edit_books_btn_text, reply_markup=reply_keyboard)

            message_id = user_data.pop(MESSAGE_ID)
            user_data.clear()
            user_data[STATE] = EDIT_BOOKS
            user_data[MESSAGE_ID] = message_id
            return EDIT_BOOKS


def back_to_editing_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    photo = PHOTOS_URL + 'kitappuz_photo.jpg'
    caption = "Tahrirlash uchun kitobni tanlang:"
    inline_keyboard = InlineKeyboard(edit_books_keyboard, user[LANG], data=get_all_books()).get_keyboard()
    state = EDIT_BOOKS

    reply_keyboard = ReplyKeyboard(back_keyboard, user[LANG]).get_keyboard()
    update.message.reply_text('📚 ' + edit_books_btn_text, reply_markup=reply_keyboard)

    if 'book_id' in user_data:
        book = get_book(user_data['book_id'])
        caption = get_book_layout(book, user[LANG])
        photo = book[PHOTO]
        inline_keyboard = InlineKeyboard(edit_book_keyboard, user[LANG], data=book).get_keyboard()
        state = EDIT_BOOK
    else:
        user_data.clear()
    # this try except used for send old books' photo like rework.jpg, drive.jpg etc.
    try:
        message = update.message.reply_photo(photo, caption, reply_markup=inline_keyboard)
    except TelegramError:
        message = update.message.reply_photo(PHOTOS_URL + photo, caption, reply_markup=inline_keyboard)
    delete_message_by_message_id(context, user)
    user_data[STATE] = state
    user_data[MESSAGE_ID] = message.message_id
    return state


def edit_books_conversation_fallback(update: Update, context: CallbackContext):
    return edit_contactus_conversation_fallback(update, context)


edit_books_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(f'{edit_books_btn_text}$'), edit_books_conversation_callback)],

    states={
        EDIT_BOOKS: [CallbackQueryHandler(edit_books_callback, pattern=r'^(edit_book_\d+|add_book)$')],

        EDIT_BOOK: [CallbackQueryHandler(edit_book_callback, pattern=r'^(edit_\w+|back|delete_book)$')],

        EDIT_BOOK_PHOTO: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command) | Filters.photo, edit_book_photo_callback)
        ],
        EDIT_BOOK_TITLE: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command), edit_book_title_callback)
        ],
        EDIT_BOOK_PRICE: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command), edit_book_price_callback)
        ],
        EDIT_BOOK_AUTHOR: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command), edit_book_author_callback)
        ],
        EDIT_BOOK_LANG: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command), edit_book_lang_callback)
        ],
        EDIT_BOOK_TRANSLATOR: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command), edit_book_translator_callback)
        ],
        EDIT_BOOK_COVER: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command), edit_book_cover_callback)
        ],
        EDIT_BOOK_URL: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command) | Filters.entity('url'), edit_book_url_callback)
        ],
        EDIT_BOOK_AMOUT: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command), edit_book_amout_callback)
        ],
        EDIT_BOOK_YEAR: [
            MessageHandler(Filters.regex(not_back_to_editing_btn_pattern) & (~Filters.update.edited_message)
                           & (~Filters.command), edit_book_year_callback),
            CallbackQueryHandler(edit_book_year_callback, pattern='^next$')
        ],
        YES_NO_CONFIRMATION: [CallbackQueryHandler(yes_no_confirm_callback,
                                                   pattern=r'^(delete|continue|confirm)_[yn]_(book|adding)$')]
    },

    fallbacks=[
        MessageHandler(Filters.regex(f'{back_to_editing_btn_text}$') & (~Filters.update.edited_message)
                       & (~Filters.command), back_to_editing_callback),
        MessageHandler(Filters.text, edit_books_conversation_fallback),
    ],

    persistent=True,

    name='edit_books_conversation'
)
