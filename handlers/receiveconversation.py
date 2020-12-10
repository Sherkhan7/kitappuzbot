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

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logger = logging.getLogger()

CHOOSE = 'choose'


def receive_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    set_user_data(update.effective_user.id, user_data)
    user = user_data['user_data']

    callback_query = update.callback_query
    data = callback_query.data

    callback_query.answer()

    if data == 'receive':
        pass

    elif data == 'cancel':
        state = ConversationHandler.END
        # caption = get_basket_layout(user_data[USER_INPUT_DATA][BASKET], user[LANG])
        # inline_keyboard = InlineKeyboard(basket_keyboard, user[LANG]).get_keyboard()
        #
        # callback_query.edit_message_caption(caption, parse_mode=ParseMode.HTML, reply_markup=inline_keyboard)

    state = CHOOSE
    inline_keyboard = InlineKeyboard(choose_keyboard, user[LANG], data=['d']).get_keyboard()

    callback_query.edit_message_reply_markup(inline_keyboard)
    user_data[USER_INPUT_DATA][STATE] = state

    logger.info('user_data: %s', user_data)
    return state


def choose_callback(update: Update, context: CallbackContext):
    user_data = context.user_data
    user = user_data['user_data']

    callback_query = update.callback_query
    data = callback_query.data

    callback_query.answer()
    print(data)

    state = user_data[USER_INPUT_DATA][STATE]

    user_data[USER_INPUT_DATA][STATE] = state

    logger.info('user_data: %s', user_data)
    return state


receive_conversation_handler = ConversationHandler(

    entry_points=[],
    states={

        CHOOSE: [CallbackQueryHandler(choose_callback, pattern=r'^(yes|no)$')]

    },
    fallbacks=[],

    persistent=True,
    name='receive_conversation'
)
