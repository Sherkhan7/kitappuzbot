from telegram.ext import Updater, PicklePersistence, Defaults
from telegram import ParseMode

from config import TOKEN, BASE_URL, PORT
from errorhandler import error_handler
from handlers import *


def main():
    my_persistence = PicklePersistence(filename='my_pickle', single_file=False, store_chat_data=False)
    defaults = Defaults(parse_mode=ParseMode.HTML, allow_sending_without_reply=True, disable_web_page_preview=True)

    updater = Updater(TOKEN, persistence=my_persistence, defaults=defaults)

    updater.dispatcher.add_handler(edit_actions_conversation_handler)

    updater.dispatcher.add_handler(edit_admins_conversation_handler)

    updater.dispatcher.add_handler(edit_books_conversation_handler)

    updater.dispatcher.add_handler(edit_contactus_conversation_handler)

    updater.dispatcher.add_handler(sendpost_conversation_handler)

    updater.dispatcher.add_handler(command_handler)

    updater.dispatcher.add_handler(books_conversation_handler)

    updater.dispatcher.add_handler(registration_conversation_handler)

    updater.dispatcher.add_handler(message_handler)

    updater.dispatcher.add_handler(callback_query_handler)

    # ...and the error handler
    updater.dispatcher.add_error_handler(error_handler)

    # updater.start_polling()
    updater.start_webhook(port=PORT, url_path=TOKEN, webhook_url=BASE_URL + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
