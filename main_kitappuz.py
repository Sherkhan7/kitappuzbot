from telegram.ext import Updater, PicklePersistence
from config import TOKEN
from handlers import (message_handler, inline_keyboard_handler, registration_conversation_handler,
                      books_conversation_handler)


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

    # updater.start_polling()
    # updater.idle()

    updater.start_webhook(listen='127.0.0.1', port=5004, url_path=TOKEN)
    updater.bot.set_webhook(url='https://cardel.ml/' + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
