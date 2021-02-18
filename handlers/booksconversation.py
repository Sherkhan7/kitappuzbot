from telegram import Update, InputMediaPhoto, ParseMode, ReplyKeyboardRemove
from telegram.ext import MessageHandler, ConversationHandler, CallbackContext, Filters, CallbackQueryHandler

from config import PHOTOS_URL, ACTIVE_ADMINS
from DB import insert_data, get_book, insert_order_items

from helpers import set_user_data, wrap_tags
from filters import phone_number_filter
from globalvariables import *
from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *
from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from layouts import get_book_layout, get_basket_layout, get_phone_number_layout, get_action_layout

import logging

logger = logging.getLogger()

BOOKS, BOOK, ORDER, BASKET = ['books', 'book', 'order', 'basket']


def books_conversation_callback(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user_data = context.user_data
    set_user_data(update.effective_user.id, user_data)
    user = user_data['user_data']

    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())

    photo = PHOTOS_URL + 'kitappuz_photo.jpg'
    inline_keyboard = InlineKeyboard(books_keyboard, user[LANG]).get_keyboard()
    message = update.message.reply_photo(photo, reply_markup=inline_keyboard)

    state = BOOKS

    if USER_INPUT_DATA not in user_data:
        user_data[USER_INPUT_DATA] = dict()

    user_data[USER_INPUT_DATA][STATE] = state
    user_data[USER_INPUT_DATA][MESSAGE_ID] = message.message_id

    # logger.info('user_data: %s', user_data)
    return state


def mega_action_callback(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user_data = context.user_data
    set_user_data(update.effective_user.id, user_data)
    user = user_data['user_data']

    books = {6: 1, 4: 1, 2: 1, 3: 1, 5: 1, 1: 1}

    inline_keyboard = InlineKeyboard(basket_keyboard, user[LANG]).get_keyboard()
    inline_keyboard.inline_keyboard.pop(0)

    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
    message = update.message.reply_photo(PHOTOS_URL + '5+1_action.jpg', get_action_layout(books, data=' '),
                                         reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

    state = BASKET

    if USER_INPUT_DATA not in user_data:
        user_data[USER_INPUT_DATA] = dict()

    user_data[USER_INPUT_DATA][STATE] = state
    user_data[USER_INPUT_DATA][MESSAGE_ID] = message.message_id
    user_data[USER_INPUT_DATA][BASKET] = books
    user_data[USER_INPUT_DATA]['mega_action'] = True

    # logger.info('user_data: %s', user_data)
    return state


def books_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = user_data['user_data']

    callback_query = update.callback_query
    data = callback_query.data

    callback_query.answer()

    if data == 'basket':

        caption = get_basket_layout(user_data[USER_INPUT_DATA][BASKET], user[LANG])
        inline_keyboard = InlineKeyboard(basket_keyboard, user[LANG]).get_keyboard()

        callback_query.edit_message_caption(caption, parse_mode=ParseMode.HTML, reply_markup=inline_keyboard)

        state = BASKET

    else:

        book_id = data.split('_')[-1]
        book = get_book(book_id)
        caption = get_book_layout(book, user[LANG])
        user_data[USER_INPUT_DATA][BOOK] = book

        media_photo = InputMediaPhoto(PHOTOS_URL + book[PHOTO], caption=caption, parse_mode=ParseMode.HTML)
        inline_keyboard = InlineKeyboard(book_keyboard, user[LANG], data=book).get_keyboard()

        callback_query.edit_message_media(media_photo, reply_markup=inline_keyboard)

        state = BOOK

    user_data[USER_INPUT_DATA][STATE] = state

    # logger.info('user_data: %s', user_data)
    return state


def book_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = user_data['user_data']

    callback_query = update.callback_query
    data = callback_query.data

    callback_query.answer()

    if data == 'back':
        media_photo = InputMediaPhoto(PHOTOS_URL + 'kitappuz_photo.jpg')
        data = True if BASKET in user_data[USER_INPUT_DATA] else None
        inline_keyboard = InlineKeyboard(books_keyboard, user[LANG], data=data).get_keyboard()

        callback_query.edit_message_media(media_photo, reply_markup=inline_keyboard)

        del user_data[USER_INPUT_DATA][BOOK]

        state = BOOKS

    elif data == 'ordering':

        book_id = user_data[USER_INPUT_DATA][BOOK][ID]

        inline_keyboard = InlineKeyboard(order_keyboard, user[LANG], data=book_id).get_keyboard()
        callback_query.edit_message_reply_markup(inline_keyboard)

        state = ORDER

    user_data[USER_INPUT_DATA][STATE] = state

    # logger.info('user_data: %s', user_data)
    return state


def order_callback(update: Update, context: CallbackContext):
    # with open('jsons/callback_query.json', 'w') as update_file:
    #     update_file.write(update.callback_query.to_json())
    user_data = context.user_data
    user = user_data['user_data']

    callback_query = update.callback_query
    data = callback_query.data

    if data == '-' or data == '+' or data.isdigit():

        if not data.isdigit():
            button = update.callback_query.message.reply_markup.inline_keyboard[0][1]
            counter = int(button.text) - 1 if data == '-' else int(button.text) + 1

            if counter in range(1, 6):
                callback_query.answer()
                button.text = counter
                button.callback_data = str(counter)

                callback_query.edit_message_reply_markup(update.callback_query.message.reply_markup)

            else:

                alert_text = "Kechirasiz siz bitta kitobga kamida 1 ta, " \
                             "ko'pi bilan 5 ta gacha buyurtma bera olasiz \U0001F60C"
                callback_query.answer(alert_text, show_alert=True)
        else:
            callback_query.answer()

        state = user_data[USER_INPUT_DATA][STATE]

    elif data == 'back':
        callback_query.answer()
        book = user_data[USER_INPUT_DATA][BOOK]

        inline_keyboard = InlineKeyboard(book_keyboard, user[LANG], data=book).get_keyboard()
        callback_query.edit_message_reply_markup(inline_keyboard)

        state = BOOK

    elif data == 'order':

        book = user_data[USER_INPUT_DATA][BOOK]
        quantity = int(callback_query.message.reply_markup.inline_keyboard[0][1].text)

        basket = {book[ID]: quantity}

        if BASKET not in user_data[USER_INPUT_DATA]:
            user_data[USER_INPUT_DATA][BASKET] = dict()
            user_data[USER_INPUT_DATA][BASKET].update(basket)

        else:

            if book[ID] in user_data[USER_INPUT_DATA][BASKET]:

                old_quantity = user_data[USER_INPUT_DATA][BASKET][book[ID]]
                new_quantity = old_quantity + quantity

                if new_quantity > 5:
                    alert_text = "Kechirasiz siz bitta kitobga kamida 1 ta, " \
                                 "ko'pi bilan 5 ta gacha buyurtma bera olasiz \U0001F60C"
                    alert_text += f"\n\nSavatchangizda {wrap_tags(book['title'])} kitobidan " \
                                  f"{wrap_tags(str(old_quantity))} ta bor !"

                    callback_query.answer(alert_text, show_alert=True)

                    return user_data[USER_INPUT_DATA][STATE]

                else:
                    user_data[USER_INPUT_DATA][BASKET][book[ID]] = new_quantity

            else:
                user_data[USER_INPUT_DATA][BASKET].update(basket)

        callback_query.answer()

        caption = get_basket_layout(user_data[USER_INPUT_DATA][BASKET], user[LANG])
        inline_keyboard = InlineKeyboard(basket_keyboard, user[LANG]).get_keyboard()

        callback_query.edit_message_caption(caption, parse_mode=ParseMode.HTML, reply_markup=inline_keyboard)

        state = BASKET

    user_data[USER_INPUT_DATA][STATE] = state

    # logger.info('user_data: %s', user_data)
    return state


def basket_callback(update: Update, context: CallbackContext):
    # with open('jsons/callback_query.json', 'w') as update_file:
    #     update_file.write(update.callback_query.to_json())
    user_data = context.user_data
    user = user_data['user_data']

    callback_query = update.callback_query
    data = callback_query.data

    callback_query.answer()

    if data == 'continue':

        photo = PHOTOS_URL + 'kitappuz_photo.jpg'
        inline_keyboard = InlineKeyboard(books_keyboard, user[LANG], data=True).get_keyboard()

        callback_query.edit_message_media(InputMediaPhoto(photo), reply_markup=inline_keyboard)

        state = BOOKS

    elif data == 'confirmation':

        callback_query.edit_message_caption(callback_query.message.caption_html, parse_mode=ParseMode.HTML)

        text = "Siz bilan bog'lanishimiz uchun telefon raqamingizni yuboring\n"
        layout = get_phone_number_layout(user[LANG])
        repky_keyboard = ReplyKeyboard(phone_number_keyboard, user[LANG]).get_keyboard()
        text += layout

        # text = "To'liq manzilingizni yuboring:\n"
        # example = wrap_tags('Masalan: Toshkent shahri, Chilonzor tumani, XX-uy, XX-xonadon')
        # text += example

        callback_query.message.reply_html(text, reply_markup=repky_keyboard)

        # Remove the PHONE_NUMBER STATE
        state = PHONE_NUMBER

    user_data[USER_INPUT_DATA][STATE] = state

    # logger.info('user_data: %s', user_data)
    return state


# def address_callback(update: Update, context: CallbackContext):
#     # with open('jsons/callback_query.json', 'w') as update_file:
#     #     update_file.write(update.callback_query.to_json())
#     user_data = context.user_data
#     user = user_data['user_data']
#
#     user_data[USER_INPUT_DATA][ADDRESS] = update.message.text
#     text = "Geolokatsiyangizni yuboring.\n" \
#            f"Yoki bu bosqichni o'tkazib yuborinsh uchun {wrap_tags('keyingisi')} tugmasini bosing"
#
#     reply_keyboard = ReplyKeyboard(location_keyboard, user[LANG]).get_keyboard()
#     update.message.reply_html(text, reply_markup=reply_keyboard)
#
#     state = GEOLOCATION
#
#     user_data[USER_INPUT_DATA][STATE] = state
#
#     logger.info('user_data: %s', user_data)
#     return state


# def geolocation_callback(update: Update, context: CallbackContext):
#     # with open('jsons/callback_query.json', 'w') as update_file:
#     #     update_file.write(update.callback_query.to_json())
#     user_data = context.user_data
#     user = user_data['user_data']
#
#     if update.message.location:
#         user_data[USER_INPUT_DATA][GEOLOCATION] = update.message.location.to_dict()
#     else:
#         user_data[USER_INPUT_DATA][GEOLOCATION] = None
#
#     text = "Siz bilan bog'lanishimiz uchun telefon raqamingizni yuboring\n"
#     layout = get_phone_number_layout(user[LANG])
#     repky_keyboard = ReplyKeyboard(phone_number_keyboard, user[LANG]).get_keyboard()
#     text += layout
#
#     update.message.reply_html(text, reply_markup=repky_keyboard)
#
#     state = PHONE_NUMBER
#
#     user_data[USER_INPUT_DATA][STATE] = state
#
#     logger.info('user_data: %s', user_data)
#     return state


def phone_callback(update: Update, context: CallbackContext):
    # with open('jsons/callback_query.json', 'w') as update_file:
    #     update_file.write(update.callback_query.to_json())
    user_data = context.user_data
    user = user_data['user_data']

    phone_number = update.message.contact.phone_number if update.message.contact else update.message.text
    phone_number = phone_number_filter(phone_number)

    if not phone_number:

        error_text = "Telefon raqami xato formatda yuborildi\n"
        layout = get_phone_number_layout(user[LANG])
        error_text += layout

        update.message.reply_html(error_text, quote=True)

        state = user_data[USER_INPUT_DATA][STATE]

    else:

        user_data[USER_INPUT_DATA][PHONE_NUMBER] = phone_number

        # geo = user_data[USER_INPUT_DATA][GEOLOCATION] if GEOLOCATION in user_data[USER_INPUT_DATA] else None
        geo = None

        text = 'Buyurtmangizni tasdiqlang'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

        layout = get_basket_layout(user_data[USER_INPUT_DATA][BASKET], user[LANG])

        if 'mega_action' in user_data[USER_INPUT_DATA]:
            layout = get_action_layout(user_data[USER_INPUT_DATA][BASKET], data=' ')

        layout += f'\nMijoz: {wrap_tags(user[FULLNAME])}\n' \
                  f'Tel: {wrap_tags(user_data[USER_INPUT_DATA][PHONE_NUMBER])}\n'
        layout += f'Telegram: {wrap_tags("@" + user[USERNAME])}' if user[USERNAME] else ''

        inline_keyboard = InlineKeyboard(confirm_keyboard, user[LANG], data=geo).get_keyboard()

        message = update.message.reply_html(layout, reply_markup=inline_keyboard)
        user_data[USER_INPUT_DATA][MESSAGE_ID] = message.message_id

        state = CONFIRMATION

    user_data[USER_INPUT_DATA][STATE] = state

    # logger.info('user_data: %s', user_data)

    return state


def confirmation_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = user_data['user_data']

    callback_query = update.callback_query
    data = callback_query.data

    callback_query.answer()

    if data == 'cancel':
        edit_text = callback_query.message.text_html.split('\n')
        edit_text[0] = wrap_tags(edit_text[0] + f' [Bekor qilingan]')
        edit_text = '\n'.join(edit_text)

        callback_query.edit_message_text(edit_text, parse_mode=ParseMode.HTML)

        reply_keyboard = ReplyKeyboard(client_menu_keyboard, user[LANG]).get_keyboard()
        callback_query.message.reply_text('\U0000274C Buyurma bekor qilindi !', quote=True)
        callback_query.message.reply_text('Menyu', reply_markup=reply_keyboard)

        state = ConversationHandler.END

        # logger.info('user_data: %s', user_data)

    elif data == 'confirm':
        # geo = user_data[USER_INPUT_DATA][GEOLOCATION]
        # geo = json.dumps(geo) if geo else None
        geo = None

        order_data = {
            USER_ID: user[ID],
            STATUS: 'waiting',
            MESSAGE_ID: user_data[USER_INPUT_DATA][MESSAGE_ID],
            # ADDRESS: user_data[USER_INPUT_DATA][ADDRESS],
            # GEOLOCATION: geo,
            PHONE_NUMBER: user_data[USER_INPUT_DATA][PHONE_NUMBER],
            USER_TG_ID: user[TG_ID]
        }

        if 'mega_action' in user_data[USER_INPUT_DATA]:
            order_data.update({'with_action': True})

        order_id = insert_data(order_data, 'orders')

        order_items_data = {
            ORDER_ID: order_id,
            BASKET: user_data[USER_INPUT_DATA][BASKET]
        }

        result = insert_order_items(dict(order_items_data), 'order_items')

        if result > 0:
            # print(callback_query.message.text_html)

            text_for_admin = callback_query.message.text_html.split('\n')
            text_for_admin[0] = f'\U0001F194 {order_id} {wrap_tags("[Yangi buyurtma]")}'
            text_for_admin += [f'Status: {wrap_tags("qabul qilish kutilmoqda")}']
            text_for_admin = '\n'.join(text_for_admin)
            text_for_client = text_for_admin

            inline_keyboard = InlineKeyboard(orders_keyboard, user[LANG], data=[geo, order_id]).get_keyboard()

            for ADMIN in ACTIVE_ADMINS:
                context.bot.send_message(ADMIN, text_for_admin, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

            callback_query.edit_message_text(text_for_client, parse_mode=ParseMode.HTML)

            text = "Buyurtmangiz administratorga yetkazildi.\n" \
                   "Tez orada siz bilan bog'lanamiz \U0000263A\n\n" \
                   "Buyurtmangiz uchun tashakkur !"
            reply_keyboard = ReplyKeyboard(client_menu_keyboard, user[LANG]).get_keyboard()

            callback_query.message.reply_text(text, reply_markup=reply_keyboard)

        state = ConversationHandler.END

    # logger.info('user_data: %s', user_data)
    del user_data[USER_INPUT_DATA]

    return state


def cancel_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = user_data['user_data']

    text = update.message.text

    if text == '/menu' or text == '/cancel':
        context.bot.edit_message_reply_markup(user[TG_ID], user_data[USER_INPUT_DATA][MESSAGE_ID])

        text = 'Menu' if text == '/menu' else '\U0000274C Bekor qilindi !'
        reply_keyboard = ReplyKeyboard(client_menu_keyboard, user[LANG]).get_keyboard()

        update.message.reply_text(text, reply_markup=reply_keyboard)

        del user_data[USER_INPUT_DATA]
        state = ConversationHandler.END

    else:
        update.message.reply_text("Siz hozir \U0001F4DA Kitoblar bo'limidasiz.\n"
                                  "Bu bo'limdan chiqish uchun /cancel yoki /menu kommandasini yuboring.", quote=True)

        state = user_data[USER_INPUT_DATA][STATE]

    return state


books_conversation_handler = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex('Kitoblar$'), books_conversation_callback),

        MessageHandler(Filters.regex('MEGA AKSIYA'), mega_action_callback)
    ],

    states={

        BOOKS: [CallbackQueryHandler(books_callback, pattern=r'^(book_\d+|basket|with_action)$')],

        BOOK: [CallbackQueryHandler(book_callback, pattern=r'^(ordering|back|ordering_action)$')],

        ORDER: [CallbackQueryHandler(order_callback, pattern=r'^(\+|\d|-|order|back)$')],

        BASKET: [CallbackQueryHandler(basket_callback, pattern=r'^(continue|confirmation)$')],

        # ADDRESS: [MessageHandler(Filters.text & (~ Filters.command), address_callback)],

        # GEOLOCATION: [MessageHandler(Filters.location | Filters.regex('keyingisi$'), geolocation_callback)],

        PHONE_NUMBER: [MessageHandler(Filters.contact | Filters.text & (~ Filters.command), phone_callback)],

        CONFIRMATION: [CallbackQueryHandler(confirmation_callback, pattern=r'^(confirm|cancel)$')]

    },
    fallbacks=[
        MessageHandler(Filters.text, cancel_callback),
    ],

    persistent=True,

    name='book_conversation'
)
