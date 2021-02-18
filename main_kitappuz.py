from telegram.ext import Updater, PicklePersistence, CallbackContext
from telegram import Update, ParseMode

from config import TOKEN, DEVELOPER_CHAT_ID
from handlers import (
    message_handler,
    inline_keyboard_handler,
    registration_conversation_handler,
    books_conversation_handler
)

import logging
import traceback
import html
import json

# Setting up logging basic config for standart output
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')

# Getting logger
logger = logging.getLogger()


def error_handler(update:Update, context: CallbackContext):

    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        f'An exception was raised while handling an update:\n'
        f'{"".ljust(100, "*")}'
        f'<pre>update = {html.escape(json.dumps(update.to_dict(), indent=4, ensure_ascii=False))}'
        f'</pre>\n'
        f'{"".ljust(100, "*")}'
        # f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n'
        # f'{"".ljust(100, "*")}'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n'
        f'{"".ljust(100, "*")}'
        f'<pre>{html.escape(tb_string)}</pre>\n'
        f'{"".ljust(100, "*")}'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


def main():
    my_persistence = PicklePersistence(filename='my_pickle', single_file=False, store_chat_data=False)

    updater = Updater(TOKEN, persistence=my_persistence)

    #
    # updater.dispatcher.add_handler(changedataconversation_handler)
    #
    updater.dispatcher.add_handler(books_conversation_handler)

    updater.dispatcher.add_handler(registration_conversation_handler)

    updater.dispatcher.add_handler(message_handler)

    updater.dispatcher.add_handler(inline_keyboard_handler)

    # ...and the error handler
    updater.dispatcher.add_error_handler(error_handler)

    # updater.start_polling()
    # updater.idle()

    updater.start_webhook(listen='127.0.0.1', port=5004, url_path=TOKEN)
    updater.bot.set_webhook(url='https://cardel.ml/' + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
