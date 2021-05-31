import logging

from telegram import Update, InputMediaPhoto, ParseMode, ReplyKeyboardRemove, TelegramError
from telegram.ext import MessageHandler, ConversationHandler, CallbackContext, Filters, CallbackQueryHandler

from config import *
from globalvariables import *
from layouts import *
from helpers import wrap_tags
from filters import phone_number_filter
from DB import insert_data, get_book, insert_order_items, get_user

from replykeyboards import ReplyKeyboard
from replykeyboards.replykeyboardvariables import *

from inlinekeyboards import InlineKeyboard
from inlinekeyboards.inlinekeyboardvariables import *

logger = logging.getLogger()


def books_conversation_callback(update: Update, context: CallbackContext):
    # with open('update.json', 'w') as update_file:
    #     update_file.write(update.to_json())
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
    inline_keyboard = InlineKeyboard(books_keyboard, user[LANG]).get_keyboard()
    message = update.message.reply_photo(PHOTOS_URL + 'kitappuz_photo.jpg', reply_markup=inline_keyboard)

    state = BOOKS
    user_data[STATE] = state
    user_data[MESSAGE_ID] = message.message_id
    # logger.info('user_data: %s', user_data)
    return state


def mega_action_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data

    books = {7: 1, 6: 1, 4: 1, 2: 1, 3: 1, 5: 1, 1: 1}
    inline_keyboard = InlineKeyboard(basket_keyboard, user[LANG]).get_keyboard()
    inline_keyboard.inline_keyboard.pop(0)

    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())
    message = update.message.reply_photo(PHOTOS_URL + '6+1_action.jpg', get_action_layout(books),
                                         reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
    state = BASKET
    user_data[STATE] = state
    user_data[MESSAGE_ID] = message.message_id
    user_data[BASKET] = books
    user_data['mega_action'] = True
    # logger.info('user_data: %s', user_data)
    return state


def books_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data
    callback_query.answer()

    if data == 'basket':
        caption = get_basket_layout(user_data[BASKET], user[LANG])
        inline_keyboard = InlineKeyboard(basket_keyboard, user[LANG]).get_keyboard()
        try:
            callback_query.edit_message_caption(caption, parse_mode=ParseMode.HTML, reply_markup=inline_keyboard)
        except TelegramError:
            pass
        state = BASKET

    else:
        book_id = data.split('_')[-1]
        book = get_book(book_id)
        caption = get_book_layout(book, user[LANG])
        media_photo = InputMediaPhoto(PHOTOS_URL + book[PHOTO], caption=caption, parse_mode=ParseMode.HTML)
        inline_keyboard = InlineKeyboard(book_keyboard, user[LANG], data=book).get_keyboard()
        try:
            callback_query.edit_message_media(media_photo, reply_markup=inline_keyboard)
        except TelegramError:
            pass
        user_data[BOOK] = book
        state = BOOK

    user_data[STATE] = state
    # logger.info('user_data: %s', user_data)
    return state


def book_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data
    callback_query.answer()

    if data == 'back':
        media_photo = InputMediaPhoto(PHOTOS_URL + 'kitappuz_photo.jpg')
        data = True if BASKET in user_data else None
        inline_keyboard = InlineKeyboard(books_keyboard, user[LANG], data=data).get_keyboard()
        try:
            callback_query.edit_message_media(media_photo, reply_markup=inline_keyboard)
        except TelegramError:
            pass
        del user_data[BOOK]
        state = BOOKS

    elif data == 'ordering':
        book_id = user_data[BOOK][ID]
        inline_keyboard = InlineKeyboard(order_keyboard, user[LANG], data=book_id).get_keyboard()
        try:
            callback_query.edit_message_reply_markup(inline_keyboard)
        except TelegramError:
            pass
        state = ORDER

    user_data[STATE] = state
    # logger.info('user_data: %s', user_data)
    return state


def order_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
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
                try:
                    callback_query.edit_message_reply_markup(update.callback_query.message.reply_markup)
                except TelegramError:
                    pass

            else:
                alert_text = "Kechirasiz siz bitta kitobga kamida 1 ta, " \
                             "ko'pi bilan 5 ta gacha buyurtma bera olasiz \U0001F60C"
                callback_query.answer(alert_text, show_alert=True)

        else:
            callback_query.answer()

        state = user_data[STATE]

    elif data == 'back':
        callback_query.answer()
        book = user_data[BOOK]
        inline_keyboard = InlineKeyboard(book_keyboard, user[LANG], data=book).get_keyboard()
        try:
            callback_query.edit_message_reply_markup(inline_keyboard)
        except TelegramError:
            pass

        state = BOOK

    elif data == 'order':
        book = user_data[BOOK]
        quantity = int(callback_query.message.reply_markup.inline_keyboard[0][1].text)
        basket = {book[ID]: quantity}

        if BASKET not in user_data:
            user_data[BASKET] = dict()
            user_data[BASKET].update(basket)

        else:
            if book[ID] in user_data[BASKET]:
                old_quantity = user_data[BASKET][book[ID]]
                new_quantity = old_quantity + quantity

                if new_quantity > 5:
                    alert_text = "Kechirasiz siz bitta kitobga kamida 1 ta, " \
                                 "ko'pi bilan 5 ta gacha buyurtma bera olasiz \U0001F60C"
                    alert_text += f"\n\nSavatchangizda {wrap_tags(book['title'])} kitobidan " \
                                  f"{wrap_tags(str(old_quantity))} ta bor !"
                    callback_query.answer(alert_text, show_alert=True)
                    return user_data[STATE]

                else:
                    user_data[BASKET][book[ID]] = new_quantity

            else:
                user_data[BASKET].update(basket)

        callback_query.answer()
        caption = get_basket_layout(user_data[BASKET], user[LANG])
        inline_keyboard = InlineKeyboard(basket_keyboard, user[LANG]).get_keyboard()
        try:
            callback_query.edit_message_caption(caption, parse_mode=ParseMode.HTML, reply_markup=inline_keyboard)
        except TelegramError:
            pass
        state = BASKET

    user_data[STATE] = state
    # logger.info('user_data: %s', user_data)
    return state


def basket_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data
    callback_query.answer()

    if data == 'continue':
        inline_keyboard = InlineKeyboard(books_keyboard, user[LANG], data=True).get_keyboard()
        try:
            callback_query.edit_message_media(InputMediaPhoto(PHOTOS_URL + 'kitappuz_photo.jpg'), inline_keyboard)
        except TelegramError:
            pass
        state = BOOKS

    elif data == 'confirmation':
        try:
            callback_query.edit_message_caption(callback_query.message.caption_html, parse_mode=ParseMode.HTML)
        except TelegramError:
            pass
        text = "Siz bilan bog'lanishimiz uchun telefon raqamingizni yuboring\n"
        layout = get_phone_number_layout(user[LANG])
        repky_keyboard = ReplyKeyboard(phone_number_keyboard, user[LANG]).get_keyboard()
        text += layout
        # text = "To'liq manzilingizni yuboring:\n"
        # example = wrap_tags('Masalan: Toshkent shahri, Chilonzor tumani, XX-uy, XX-xonadon')
        # text += example
        callback_query.message.reply_html(text, reply_markup=repky_keyboard)
        state = PHONE_NUMBER

    user_data[STATE] = state
    # logger.info('user_data: %s', user_data)
    return state


# def address_callback(update: Update, context: CallbackContext):
#     # with open('jsons/callback_query.json', 'w') as update_file:
#     #     update_file.write(update.callback_query.to_json())
#     user_data = context.user_data
#     user = user_data['user_data']
#
#     user_data[ADDRESS] = update.message.text
#     text = "Geolokatsiyangizni yuboring.\n" \
#            f"Yoki bu bosqichni o'tkazib yuborinsh uchun {wrap_tags('keyingisi')} tugmasini bosing"
#
#     reply_keyboard = ReplyKeyboard(location_keyboard, user[LANG]).get_keyboard()
#     update.message.reply_html(text, reply_markup=reply_keyboard)
#
#     state = GEOLOCATION
#
#     user_data[STATE] = state
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
#         user_data[GEOLOCATION] = update.message.location.to_dict()
#     else:
#         user_data[GEOLOCATION] = None
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
#     user_data[STATE] = state
#
#     logger.info('user_data: %s', user_data)
#     return state


def phone_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    phone_number = update.message.contact.phone_number if update.message.contact else update.message.text
    phone_number = phone_number_filter(phone_number)

    if not phone_number:
        error_text = "Telefon raqami xato formatda yuborildi\n"
        layout = get_phone_number_layout(user[LANG])
        error_text += layout
        update.message.reply_html(error_text, quote=True)
        state = user_data[STATE]

    else:
        user_data[PHONE_NUMBER] = phone_number
        # geo = user_data[GEOLOCATION] if GEOLOCATION in user_data else None
        geo = None
        text = 'Buyurtmangizni tasdiqlang'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

        layout = get_basket_layout(user_data[BASKET], user[LANG])
        if 'mega_action' in user_data:
            layout = get_action_layout(user_data[BASKET])
        layout += f'\nMijoz: {wrap_tags(user[FULLNAME])}\n' \
                  f'Tel: {wrap_tags(user_data[PHONE_NUMBER])}\n'
        layout += f'Telegram: {wrap_tags("@" + user[USERNAME])}' if user[USERNAME] else ''
        inline_keyboard = InlineKeyboard(confirm_keyboard, user[LANG], data=geo).get_keyboard()
        message = update.message.reply_html(layout, reply_markup=inline_keyboard)

        user_data[MESSAGE_ID] = message.message_id
        state = CONFIRMATION

    user_data[STATE] = state
    # logger.info('user_data: %s', user_data)
    return state


def confirmation_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    callback_query = update.callback_query
    data = callback_query.data
    callback_query.answer()

    if data == 'cancel':
        edit_text = callback_query.message.text_html.split('\n')
        edit_text[0] = wrap_tags(edit_text[0] + f' [Bekor qilingan]')
        edit_text = '\n'.join(edit_text)
        try:
            callback_query.edit_message_text(edit_text, parse_mode=ParseMode.HTML)
        except TelegramError:
            pass
        reply_keyboard = ReplyKeyboard(client_menu_keyboard, user[LANG]).get_keyboard()
        callback_query.message.reply_text('\U0000274C Buyurma bekor qilindi !', quote=True)
        callback_query.message.reply_text('Menyu', reply_markup=reply_keyboard)

        state = ConversationHandler.END
        # logger.info('user_data: %s', user_data)

    elif data == 'confirm':
        geo = None
        order_data = {
            USER_ID: user[ID],
            STATUS: 'waiting',
            MESSAGE_ID: user_data[MESSAGE_ID],
            # ADDRESS: user_data[ADDRESS],
            # GEOLOCATION: geo,
            PHONE_NUMBER: user_data[PHONE_NUMBER],
            USER_TG_ID: user[TG_ID]
        }
        if 'mega_action' in user_data:
            order_data.update({'with_action': True})
        order_id = insert_data(order_data, 'orders')
        order_items_data = {
            ORDER_ID: order_id,
            BASKET: user_data[BASKET]
        }

        result = insert_order_items(dict(order_items_data), 'order_items')
        if result > 0:
            text_for_admin = callback_query.message.text_html.split('\n')
            text_for_admin[0] = f'\U0001F194 {order_id} {wrap_tags("[Yangi buyurtma]")}'
            text_for_admin += [f'Status: {wrap_tags("qabul qilish kutilmoqda")}']
            text_for_admin = '\n'.join(text_for_admin)
            text_for_client = text_for_admin
            inline_keyboard = InlineKeyboard(orders_keyboard, user[LANG], data=[geo, order_id]).get_keyboard()

            for ADMIN in ACTIVE_ADMINS:
                context.bot.send_message(ADMIN, text_for_admin, reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)
            try:
                callback_query.edit_message_text(text_for_client, parse_mode=ParseMode.HTML)
            except TelegramError:
                pass
            text = "Buyurtmangiz administratorga yetkazildi.\n" \
                   "Tez orada siz bilan bog'lanamiz \U0000263A\n\n" \
                   "Buyurtmangiz uchun tashakkur !"
            reply_keyboard = ReplyKeyboard(client_menu_keyboard, user[LANG]).get_keyboard()
            callback_query.message.reply_text(text, reply_markup=reply_keyboard)

        state = ConversationHandler.END
    # logger.info('user_data: %s', user_data)
    user_data.clear()
    return state


def cancel_callback(update: Update, context: CallbackContext):
    user = get_user(update.effective_user.id)
    user_data = context.user_data
    text = update.message.text

    if text == '/menu' or text == '/cancel':
        text = 'Menu' if text == '/menu' else '\U0000274C Bekor qilindi !'

        if user_data[STATE] != PHONE_NUMBER:
            try:
                context.bot.edit_message_reply_markup(user[TG_ID], user_data[MESSAGE_ID])
            except TelegramError:
                pass
        reply_keyboard = ReplyKeyboard(client_menu_keyboard, user[LANG]).get_keyboard()
        update.message.reply_text(text, reply_markup=reply_keyboard)

        user_data.clear()
        state = ConversationHandler.END

    else:
        update.message.reply_text("Siz hozir \U0001F4DA Kitoblar bo'limidasiz.\n"
                                  "Bu bo'limdan chiqish uchun /cancel yoki /menu kommandasini yuboring.", quote=True)
        state = user_data[STATE]
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
