import re

from telegram import Update, InputMediaPhoto, TelegramError
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
from helpers import wrap_tags
from filters import phone_number_filter
from DB import insert_data, get_book, insert_order_items, get_user
from handlers.editcontacusconversation import end_conversation
from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardtypes import reply_keyboard_types
from replykeyboards.replykeyboardvariables import *
from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

back_btn_text = reply_keyboard_types[back_keyboard]['back_btn'][f'text_uz']


def books_conversation_callback(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    reply_keyb_markup = ReplyKeyboard(back_keyboard, user[LANG]).get_markup()
    update.message.reply_text(update.message.text, reply_markup=reply_keyb_markup)

    inline_keyb_markup = InlineKeyboard(books_keyboard, user[LANG]).get_markup()
    message = update.message.reply_photo(PHOTOS_URL + 'kitappuz_photo.jpg', reply_markup=inline_keyb_markup)

    state = BOOKS
    user_data[STATE] = state
    user_data[MESSAGE_ID] = message.message_id
    return state


def books_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if callback_query.data == 'basket':
        caption = get_basket_layout(user_data[BASKET], user[LANG])
        if caption:
            inline_keyb_markup = InlineKeyboard(basket_keyboard, user[LANG]).get_markup()
            try:
                callback_query.edit_message_caption(caption, reply_markup=inline_keyb_markup)
            except TelegramError:
                pass
            state = BASKET
        else:
            inline_keyb_markup = InlineKeyboard(books_keyboard, user[LANG]).get_markup()
            callback_query.edit_message_reply_markup(inline_keyb_markup)
            callback_query.answer("Savat bo'sh 😬", show_alert=True)
            return

    else:
        book_id = callback_query.data.split('_')[-1]
        book = get_book(book_id)
        if book:
            caption = get_book_layout(book, user[LANG])
            media_photo = InputMediaPhoto(book[PHOTO], caption)
            inline_keyb_markup = InlineKeyboard(book_keyboard, user[LANG], book).get_markup()
            try:
                callback_query.edit_message_media(media_photo, reply_markup=inline_keyb_markup)
            except TelegramError:
                media_photo = InputMediaPhoto(PHOTOS_URL + book[PHOTO], caption)
                callback_query.edit_message_media(media_photo, reply_markup=inline_keyb_markup)
            user_data['book_id'] = int(book_id)
            state = BOOK
        else:
            callback_query.answer("Kitob admin tomonidan o'chirilgan 😬", show_alert=True)
            return
    callback_query.answer()
    user_data[STATE] = state
    return state


def book_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    callback_query.answer()

    if callback_query.data == 'back':
        media_photo = InputMediaPhoto(PHOTOS_URL + 'kitappuz_photo.jpg')
        data = True if BASKET in user_data else None
        inline_keyb_markup = InlineKeyboard(books_keyboard, user[LANG], data=data).get_markup()
        try:
            callback_query.edit_message_media(media_photo, reply_markup=inline_keyb_markup)
        except TelegramError:
            pass
        del user_data['book_id']
        state = BOOKS

    elif callback_query.data == 'ordering':
        inline_keyb_markup = InlineKeyboard(order_keyboard, user[LANG]).get_markup()
        try:
            callback_query.edit_message_reply_markup(inline_keyb_markup)
        except TelegramError:
            pass
        state = ORDER
    user_data[STATE] = state
    return state


def order_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query

    if callback_query.data == '-' or callback_query.data == '+' or callback_query.data.isdigit():
        if not callback_query.data.isdigit():
            button = update.callback_query.message.reply_markup.inline_keyb_markup[0][1]
            counter = int(button.text) - 1 if callback_query.data == '-' else int(button.text) + 1

            if counter in range(1, 6):
                button.text = counter
                button.callback_data = str(counter)
                try:
                    callback_query.edit_message_reply_markup(update.callback_query.message.reply_markup)
                except TelegramError:
                    pass

            else:
                alert_text = "Kechirasiz siz bitta kitobga kamida 1 ta, " \
                             "ko'pi bilan 5 ta gacha buyurtma bera olasiz 🙂"
                callback_query.answer(alert_text, show_alert=True)

        callback_query.answer()
        state = user_data[STATE]

    elif callback_query.data == 'back':
        callback_query.answer()
        book = get_book(user_data['book_id'])
        if book:
            inline_keyb_markup = InlineKeyboard(book_keyboard, user[LANG], book).get_markup()
            try:
                callback_query.edit_message_reply_markup(inline_keyb_markup)
            except TelegramError:
                pass
            state = BOOK

        else:
            media_photo = InputMediaPhoto(PHOTOS_URL + 'kitappuz_photo.jpg')
            data = True if BASKET in user_data else None
            inline_keyb_markup = InlineKeyboard(books_keyboard, user[LANG], data=data).get_markup()
            try:
                callback_query.edit_message_media(media_photo, reply_markup=inline_keyb_markup)
            except TelegramError:
                pass
            if 'book_id' in user_data:
                del user_data['book_id']
            state = BOOKS

    elif callback_query.data == 'order':
        if get_book(user_data['book_id']):
            quantity = int(callback_query.message.reply_markup.inline_keyboard[0][1].text)
            basket = {user_data['book_id']: quantity}

            if BASKET not in user_data:
                user_data[BASKET] = dict()
                user_data[BASKET].update(basket)

            else:
                if user_data['book_id'] not in user_data[BASKET]:
                    user_data[BASKET].update(basket)

                else:
                    old_quantity = user_data[BASKET][user_data['book_id']]
                    new_quantity = old_quantity + quantity

                    if new_quantity > 5:
                        alert_text = "Kechirasiz siz bitta kitobga kamida 1 ta, " \
                                     "ko'pi bilan 5 ta gacha buyurtma bera olasiz 🙂"
                        callback_query.answer(alert_text, show_alert=True)
                        return user_data[STATE]
                    user_data[BASKET][user_data['book_id']] = new_quantity

            callback_query.answer()
            caption = get_basket_layout(user_data[BASKET], user[LANG])
            inline_keyb_markup = InlineKeyboard(basket_keyboard, user[LANG]).get_markup()
            try:
                callback_query.edit_message_caption(caption, reply_markup=inline_keyb_markup)
            except TelegramError:
                pass
            state = BASKET

        else:
            callback_query.answer("❗ Kechirasiz siz bu kitobga buyurtma bera olmaysiz !\n\n"
                                  "Kitob admin tamonidan o'chirilgan 😬", show_alert=True)
            state = user_data[STATE]

    user_data[STATE] = state
    return state


def basket_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    callback_query.answer()

    if callback_query.data == 'continue':
        inline_keyb_markup = InlineKeyboard(books_keyboard, user[LANG], data=True).get_markup()
        try:
            callback_query.edit_message_media(InputMediaPhoto(PHOTOS_URL + 'kitappuz_photo.jpg'), inline_keyb_markup)
        except TelegramError:
            pass
        state = BOOKS

    elif callback_query.data == 'confirmation':
        try:
            callback_query.edit_message_reply_markup()
        except TelegramError:
            pass
        text = "Siz bilan bog'lanishimiz uchun telefon raqamingizni yuboring\n"
        layout = get_phone_number_layout(user[LANG])
        repky_keyboard = ReplyKeyboard(phone_number_keyboard, user[LANG]).get_markup()
        text += layout
        callback_query.message.reply_text(text, reply_markup=repky_keyboard)
        state = PHONE_NUMBER

    user_data[STATE] = state
    return state


def phone_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    phone_number = update.message.contact.phone_number if update.message.contact else update.message.text
    phone_number = phone_number_filter(phone_number)

    if not phone_number:
        error_text = "Telefon raqami xato formatda yuborildi\n"
        layout = get_phone_number_layout(user[LANG])
        error_text += layout
        update.message.reply_text(error_text, quote=True)
        state = user_data[STATE]

    else:
        user_data[PHONE_NUMBER] = phone_number
        layout = get_basket_layout(user_data[BASKET], user[LANG])
        if layout:
            text = 'Buyurtmangizni tasdiqlang'
            reply_keyb_markup = ReplyKeyboard(back_keyboard, user[LANG]).get_markup()
            update.message.reply_text(text, reply_markup=reply_keyb_markup)

            layout += f'\nMijoz: {wrap_tags(user[FULLNAME])}\n' \
                      f'Tel: {wrap_tags(user_data[PHONE_NUMBER])}\n'
            layout += f'Telegram: {wrap_tags("@" + user[USERNAME])}' if user[USERNAME] else ''
            inline_keyb_markup = InlineKeyboard(confirm_keyboard, user[LANG]).get_markup()
            message = update.message.reply_text(layout, reply_markup=inline_keyb_markup)
            state = CONFIRMATION
        else:
            reply_keyb_markup = ReplyKeyboard(back_keyboard, user[LANG]).get_markup()
            update.message.reply_text("Savat bo'sh 😬", reply_markup=reply_keyb_markup)
            if BASKET in user_data:
                del user_data[BASKET]
            inline_keyb_markup = InlineKeyboard(books_keyboard, user[LANG]).get_markup()
            message = update.message.reply_photo(PHOTOS_URL + 'kitappuz_photo.jpg', reply_markup=inline_keyb_markup)
            state = BOOKS
        user_data[MESSAGE_ID] = message.message_id

    user_data[STATE] = state
    return state


def confirmation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    callback_query.answer()

    if callback_query.data == 'cancel':
        edit_text = callback_query.message.text_html.split('\n')
        edit_text[0] = wrap_tags(edit_text[0] + f' [Bekor qilingan]')
        edit_text = '\n'.join(edit_text)
        try:
            callback_query.edit_message_text(edit_text)
        except TelegramError:
            pass
        reply_keyb_markup = ReplyKeyboard(client_menu_keyboard, user[LANG]).get_markup()
        callback_query.message.reply_text('❌ Buyurma bekor qilindi !', quote=True)
        callback_query.message.reply_text('📖 Menyu', reply_markup=reply_keyb_markup)

    elif callback_query.data == 'confirm':
        order_data = {
            USER_ID: user[ID],
            STATUS: 'waiting',
            MESSAGE_ID: user_data[MESSAGE_ID],
            PHONE_NUMBER: user_data[PHONE_NUMBER],
            USER_TG_ID: user[TG_ID]
        }
        order_id = insert_data(order_data, 'orders')
        data_values = [
            tuple([order_id, book_id, quantity])
            # check book for removed or not
            for (book_id, quantity) in user_data[BASKET].items() if get_book(book_id)
        ]
        if insert_order_items(data_values, [ORDER_ID, 'book_id', 'quantity'], 'order_items'):
            text_for_admin = callback_query.message.text_html.split('\n')
            text_for_admin[0] = f'🆔 {order_id} {wrap_tags("[Yangi buyurtma]")}'
            text_for_admin += [f'Status: {wrap_tags("qabul qilish kutilmoqda")}']
            text_for_admin = '\n'.join(text_for_admin)
            text_for_client = text_for_admin
            inline_keyb_markup = InlineKeyboard(orders_keyboard, user[LANG], order_id).get_markup()

            for ADMIN in ACTIVE_ADMINS:
                context.bot.send_message(ADMIN, text_for_admin, reply_markup=inline_keyb_markup)
            try:
                callback_query.edit_message_text(text_for_client)
            except TelegramError:
                pass
            text = "Buyurtmangiz administratorga yetkazildi.\nTez orada siz bilan bog'lanamiz 😉\n\n" \
                   "Buyurtmangiz uchun tashakkur !"
            reply_keyb_markup = ReplyKeyboard(client_menu_keyboard, user[LANG]).get_markup()
            callback_query.message.reply_text(text, reply_markup=reply_keyb_markup)

    user_data.clear()
    return ConversationHandler.END


def book_conversation_fallback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    back_obj = re.search(f"({back_btn_text})$", update.message.text)

    if back_obj or update.message.text == '/cancel' or update.message.text == '/start' \
            or update.message.text == '/menu':
        text = "📖 Menyu"
        keyboard = admin_menu_keyboard if user[IS_ADMIN] else client_menu_keyboard
        return end_conversation(update, context, user, text, keyboard)


books_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex('Kitoblar$'), books_conversation_callback)],

    states={
        BOOKS: [CallbackQueryHandler(books_callback, pattern=r'^(book_\d+|basket|with_action)$')],

        BOOK: [CallbackQueryHandler(book_callback, pattern=r'^(ordering|back|ordering_action)$')],

        ORDER: [CallbackQueryHandler(order_callback, pattern=r'^([+-]|\d|order|back)$')],

        BASKET: [CallbackQueryHandler(basket_callback, pattern=r'^(continue|confirmation)$')],

        PHONE_NUMBER: [MessageHandler(Filters.contact | Filters.text & (~Filters.update.edited_message)
                                      & (~ Filters.command), phone_callback)],

        CONFIRMATION: [CallbackQueryHandler(confirmation_callback, pattern=r'^(confirm|cancel)$')]
    },
    fallbacks=[
        MessageHandler(Filters.text, book_conversation_fallback),
    ],

    persistent=True,

    name='book_conversation'
)
