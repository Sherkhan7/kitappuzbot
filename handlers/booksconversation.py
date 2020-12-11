from telegram import Update, InputMediaPhoto, ParseMode, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackContext, Filters, \
    CallbackQueryHandler
from filters import *
from DB import insert_data, get_book, insert_order_items
from helpers import set_user_data
from layouts import get_basket_layout, get_phone_number_layout
from globalvariables import *
from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *
from helpers import wrap_tags
from config import PHOTOS_URL
from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *
from layouts import get_book_layout, get_basket_layout
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logger = logging.getLogger()

BOOKS = 'books'
BOOK = 'book'
ORDER = 'order'
BASKET = 'basket'


def books_conversation_callback(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user_data = context.user_data
    set_user_data(update.effective_user.id, user_data)
    user = user_data['user_data']

    photo = PHOTOS_URL + 'kitappuz_photo.jpg'
    inline_keyboard = InlineKeyboard(books_keyboard, user[LANG]).get_keyboard()

    update.message.reply_photo(photo, reply_markup=inline_keyboard)

    state = BOOKS

    if USER_INPUT_DATA not in user_data:
        user_data[USER_INPUT_DATA] = dict()

    user_data[USER_INPUT_DATA][STATE] = state

    # logger.info('user_data: %s', user_data)
    return BOOKS


def books_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = user_data['user_data']

    callback_query = update.callback_query
    data = callback_query.data

    callback_query.answer()

    if not data == 'basket':
        book = get_book(data.split('_')[-1])
        caption = get_book_layout(book, user[LANG])
        user_data[USER_INPUT_DATA][BOOK] = book

        media_photo = InputMediaPhoto(PHOTOS_URL + book[PHOTO], caption=caption, parse_mode=ParseMode.HTML)
        inline_keyboard = InlineKeyboard(book_keyboard, user[LANG], data=book).get_keyboard()

        callback_query.edit_message_media(media_photo, reply_markup=inline_keyboard)

        state = BOOK

    else:
        caption = get_basket_layout(user_data[USER_INPUT_DATA][BASKET], user[LANG])
        inline_keyboard = InlineKeyboard(basket_keyboard, user[LANG]).get_keyboard()

        callback_query.edit_message_caption(caption, parse_mode=ParseMode.HTML, reply_markup=inline_keyboard)
        state = BASKET

    user_data[USER_INPUT_DATA][STATE] = state

    logger.info('user_data: %s', user_data)
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

        if BOOK in user_data[USER_INPUT_DATA]:
            del user_data[USER_INPUT_DATA][BOOK]

        state = BOOKS

    elif data == 'ordering':
        book_id = user_data[USER_INPUT_DATA][BOOK]['id']

        inline_keyboard = InlineKeyboard(order_keyboard, user[LANG], data=book_id).get_keyboard()
        callback_query.edit_message_reply_markup(inline_keyboard)

        state = ORDER

    user_data[USER_INPUT_DATA][STATE] = state

    logger.info('user_data: %s', user_data)
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
    else:

        book = user_data[USER_INPUT_DATA].get(BOOK)
        quantity = int(callback_query.message.reply_markup.inline_keyboard[0][1].text)

        order = {book["id"]: {'quantity': quantity}}

        if BASKET not in user_data[USER_INPUT_DATA]:
            user_data[USER_INPUT_DATA][BASKET] = dict()
            user_data[USER_INPUT_DATA][BASKET].update(order)
        else:

            if book['id'] in user_data[USER_INPUT_DATA][BASKET]:

                old_quantity = user_data[USER_INPUT_DATA][BASKET][book['id']]['quantity']
                new_quantitty = old_quantity + quantity

                if new_quantitty > 5:
                    alert_text = "Kechirasiz siz bitta kitobga kamida 1 ta, " \
                                 "ko'pi bilan 5 ta gacha buyurtma bera olasiz \U0001F60C"
                    alert_text += f"\n\nSavatchangizda {book['title']} kitobidan {old_quantity} ta bor !!!"
                    callback_query.answer(alert_text, show_alert=True)

                    state = user_data[USER_INPUT_DATA][STATE]
                    user_data[USER_INPUT_DATA][STATE] = state

                    return state

                else:
                    user_data[USER_INPUT_DATA][BASKET][book['id']]['quantity'] = new_quantitty
            else:
                user_data[USER_INPUT_DATA][BASKET].update(order)

        callback_query.answer()

        caption = get_basket_layout(user_data[USER_INPUT_DATA][BASKET], user[LANG])
        inline_keyboard = InlineKeyboard(basket_keyboard, user[LANG]).get_keyboard()

        callback_query.edit_message_caption(caption, parse_mode=ParseMode.HTML, reply_markup=inline_keyboard)

        state = BASKET

    user_data[USER_INPUT_DATA][STATE] = state

    logger.info('user_data: %s', user_data)
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
    else:
        callback_query.edit_message_reply_markup(None)

        text = "To'liq manzilingizni yuboring:\n"
        example = wrap_tags('Masalan: Toshkent shahri, Chilonzor tumani, 47-uy, 18-xonadon')
        text += example

        callback_query.message.reply_text(text, parse_mode=ParseMode.HTML)

        state = ADDRESS

    user_data[USER_INPUT_DATA][STATE] = state

    logger.info('user_data: %s', user_data)
    return state


def address_callback(update: Update, context: CallbackContext):
    # with open('jsons/callback_query.json', 'w') as update_file:
    #     update_file.write(update.callback_query.to_json())
    user_data = context.user_data
    user = user_data['user_data']

    user_data[USER_INPUT_DATA][ADDRESS] = update.message.text
    text = "Geolokatsiyangizni yuboring.\n" \
           f"Yoki bu bosqichni o'tkazib yuborinsh uchun {wrap_tags('keyingisi')} tugmasini bosing"

    reply_keyboard = ReplyKeyboard(location_keyboard, user[LANG]).get_keyboard()
    update.message.reply_text(text, reply_markup=reply_keyboard, parse_mode=ParseMode.HTML)

    state = GEOLOCATION

    user_data[USER_INPUT_DATA][STATE] = state

    logger.info('user_data: %s', user_data)
    return state


def geolocation_callback(update: Update, context: CallbackContext):
    # with open('jsons/callback_query.json', 'w') as update_file:
    #     update_file.write(update.callback_query.to_json())
    user_data = context.user_data
    user = user_data['user_data']

    if update.message.location:
        user_data[USER_INPUT_DATA][GEOLOCATION] = update.message.location.to_dict()
    else:
        user_data[USER_INPUT_DATA][GEOLOCATION] = None

    text = "Siz bilan bog'lanishimiz uchun telefon raqamingizni yuboring\n"
    layout = get_phone_number_layout(user[LANG])
    repky_keyboard = ReplyKeyboard(phone_number_keyboard, user[LANG]).get_keyboard()
    text += layout

    update.message.reply_text(text, reply_markup=repky_keyboard, parse_mode=ParseMode.HTML)

    state = PHONE_NUMBER

    user_data[USER_INPUT_DATA][STATE] = state

    logger.info('user_data: %s', user_data)
    return state


def phone_callback(update: Update, context: CallbackContext):
    # with open('jsons/callback_query.json', 'w') as update_file:
    #     update_file.write(update.callback_query.to_json())
    user_data = context.user_data
    user = user_data['user_data']

    if update.message.contact:
        phone_number = phone_number_filter(update.message.contact.phone_number)
    else:
        phone_number = phone_number_filter(update.message.text)

    if not phone_number:
        error_text = "Telefon raqami xato formatda yuborldi\n"
        layout = get_phone_number_layout(user[LANG])
        error_text += layout

        update.message.reply_text(error_text, parse_mode=ParseMode.HTML, quote=True)

        state = user_data[USER_INPUT_DATA][STATE]
    else:
        user_data[USER_INPUT_DATA][PHONE_NUMBER] = phone_number

        geo = user_data[USER_INPUT_DATA][GEOLOCATION] if GEOLOCATION in user_data[USER_INPUT_DATA] else None
        text = 'Buyurtmangizni tasdiqlang'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

        layout = get_basket_layout(user_data[USER_INPUT_DATA][BASKET], user[LANG])
        inline_keyboard = InlineKeyboard(confirm_keyboard, user[LANG], data=geo).get_keyboard()

        message = update.message.reply_text(layout, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
        user_data[USER_INPUT_DATA][MESSAGE_ID] = message.message_id

        state = CONFIRMATION

    user_data[USER_INPUT_DATA][STATE] = state
    logger.info('user_data: %s', user_data)
    return state


def confirmation_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = user_data['user_data']

    callback_query = update.callback_query
    data = callback_query.data

    callback_query.answer()

    if data == 'cancel':
        state = user_data[USER_INPUT_DATA][STATE]
    else:
        geo = user_data[USER_INPUT_DATA][GEOLOCATION]
        geo = json.dumps(geo) if geo else None

        order_data = {
            USER_ID: user['id'],
            STATUS: 'waiting',
            MESSAGE_ID: user_data[USER_INPUT_DATA][MESSAGE_ID],
            ADDRESS: user_data[USER_INPUT_DATA][ADDRESS],
            GEOLOCATION: geo,
            PHONE_NUMBER: user_data[USER_INPUT_DATA][PHONE_NUMBER],
            USER_TG_ID: user[TG_ID]
        }
        order_id = insert_data(order_data, 'orders')

        order_items_data = {
            ORDER_ID: order_id,
            BASKET: user_data[USER_INPUT_DATA][BASKET]
        }
        result = insert_order_items(dict(order_items_data), 'order_items')

        if result > 0:
            callback_query.edit_message_reply_markup(None)

            text = get_basket_layout(order_items_data[BASKET], user[LANG], data='Yangi buyurtma')
            text += f'\nMijoz: {wrap_tags(user[FULLNAME])}\n' \
                    f'Manzil: {wrap_tags(order_data[ADDRESS])}\n' \
                    f'Tel: {order_data[PHONE_NUMBER]}\n'
            text += f'Telegram: {user[USERNAME]}' if user[USERNAME] else ''
            text += f'\nStatus: {order_data[STATUS]}'
            inline_keyboard = InlineKeyboard(orders_keyboard, user[LANG],
                                             data=[user_data[USER_INPUT_DATA][GEOLOCATION], order_id]).get_keyboard()

            context.bot.send_message(ADMINS[0], text, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)

            text = "Buyurtmangiz administratorga yetkazildi.\nQo'ngi'rog'imizni kuting \U0000263A"
            callback_query.message.reply_text(text)

        state = ConversationHandler.END
        del user_data[USER_INPUT_DATA]

        return state

    user_data[USER_INPUT_DATA][STATE] = state

    # logger.info('user_data: %s', user_data)
    return state


books_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex('Kitoblar$'), books_conversation_callback)],
    states={

        BOOKS: [CallbackQueryHandler(books_callback, pattern=r'^(book_\d+|basket)$')],

        BOOK: [CallbackQueryHandler(book_callback, pattern=r'^(ordering|back)$')],

        ORDER: [CallbackQueryHandler(order_callback, pattern=r'^(\+|\d|-|order_\d+|back)$')],

        BASKET: [CallbackQueryHandler(basket_callback, pattern=r'^(continue|confirmation)$')],

        ADDRESS: [MessageHandler(Filters.text & (~ Filters.command), address_callback)],

        GEOLOCATION: [MessageHandler(Filters.location | Filters.regex('keyingisi$'), geolocation_callback)],

        PHONE_NUMBER: [MessageHandler(Filters.contact | Filters.text & (~ Filters.command), phone_callback)],

        CONFIRMATION: [CallbackQueryHandler(confirmation_callback, pattern=r'^(confirm|cancel)$')]

    },
    fallbacks=[],

    persistent=True,
    name='book_conversation'
)
