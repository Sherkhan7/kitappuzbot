from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from DB import get_all_books
from globalvariables import *
from inlinekeyboards.inlinekeyboardtypes import *


class InlineKeyboard(object):
    def __init__(self, keyb_type, lang, data=None, history=None):
        self.__type = keyb_type
        self.__lang = lang
        self.__data = data
        self.__history = history
        self.__keyboard = self.__create_inline_keyboard(self.__type, self.__lang, self.__data, self.__history)

    def __create_inline_keyboard(self, keyb_type, lang, data, history):
        if keyb_type == books_keyboard:
            return self.__get_books_keyboard(data)

        elif keyb_type == book_keyboard:
            return self.__get_book_keyboard(inline_keyboard_types[keyb_type], lang, data)

        elif keyb_type == social_medias_keyboard:
            return self.__get_social_medias_keyboard(inline_keyboard_types[keyb_type], lang)

        elif keyb_type == order_keyboard:
            return self.__get_order_keyboard(inline_keyboard_types[keyb_type], lang)

        elif keyb_type == basket_keyboard:
            return self.__get_basket_keyboard(inline_keyboard_types[keyb_type], lang)

        elif keyb_type == confirm_keyboard:
            return self.__get_confirm_keyboard(inline_keyboard_types[keyb_type], lang)

        elif keyb_type == orders_keyboard:
            return self.__get_orders_keyboard(inline_keyboard_types[keyb_type], lang, data)

        elif keyb_type == yes_no_keyboard:
            return self.__get_yes_no_keyboard(inline_keyboard_types[keyb_type], lang, data)

        elif keyb_type == delivery_keyboard:
            return self.__get_delivery_keyboard(inline_keyboard_types[keyb_type], lang, data)

        elif keyb_type == paginate_keyboard:
            return self.__get_paginate_keyboard(data, history)

        elif keyb_type == edit_books_keyboard:
            return self.__get_edit_books_keyboard(inline_keyboard_types[keyb_type], lang, data)

        elif keyb_type == edit_book_keyboard:
            return self.__get_edit_book_keyboard(inline_keyboard_types[keyb_type], lang, data)

    @staticmethod
    def __get_books_keyboard(data):
        inline_keyboard = [
            [InlineKeyboardButton(f"📗 {book[TITLE]}", callback_data=f"book_{book[ID]}")]
            for book in get_all_books()
        ]
        if data:
            inline_keyboard.append([InlineKeyboardButton('🛒 Savat', callback_data='basket')])
        return InlineKeyboardMarkup(inline_keyboard)

    @staticmethod
    def __get_book_keyboard(buttons, lang, book_data):
        inline_keyboard = [
            [InlineKeyboardButton(f"{button['emoji']} {button[f'text_{lang}']}", callback_data=button['data'])]
            for button in buttons.values()]

        if book_data:
            if book_data['description_url']:
                inline_keyboard[0][0].url = book_data['description_url']
            else:
                del inline_keyboard[0]
        return InlineKeyboardMarkup(inline_keyboard)

    @staticmethod
    def __get_social_medias_keyboard(buttons, lang):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{media['emoji']} {media[f'text_{lang}']}", url=media['url'])]
            for media in buttons.values()
        ])

    @staticmethod
    def __get_order_keyboard(buttons, lang):
        order_btn_emoji = buttons['order_btn']['emoji']
        back_btn_emoji = buttons['back_btn']['emoji']
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton('-', callback_data='-'),
                InlineKeyboardButton('1', callback_data='1'),
                InlineKeyboardButton('+', callback_data='+'),
            ],
            [InlineKeyboardButton(f"{order_btn_emoji} {buttons['order_btn'][f'text_{lang}']}",
                                  callback_data=buttons['order_btn']['data'])],
            [InlineKeyboardButton(f"{back_btn_emoji} {buttons['back_btn'][f'text_{lang}']}",
                                  callback_data=buttons['back_btn']['data'])],
        ])

    @staticmethod
    def __get_basket_keyboard(buttons, lang):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{button['emoji']} {button[f'text_{lang}']}", callback_data=button['data'])]
            for button in buttons.values()
        ])

    @staticmethod
    def __get_confirm_keyboard(buttons, lang):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{button['emoji']} {button[f'text_{lang}']}", callback_data=button['data'])]
            for button in buttons.values()
        ])

    @staticmethod
    def __get_orders_keyboard(buttons, lang, data):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{button['emoji']} {button[f'text_{lang}']}",
                                  callback_data=f"{button['data']}_{data}")]
            for button in buttons.values()
        ])

    @staticmethod
    def __get_yes_no_keyboard(buttons, lang, data):
        data_0 = data[0]
        data_1 = data[-1]
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{button['emoji']} {button[f'text_{lang}']}",
                                  callback_data=f"{data_0}_{button['data']}_{data_1}")]
            for button in buttons.values()
        ])

    @staticmethod
    def __get_delivery_keyboard(buttons, lang, order_id):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{button['emoji']} {button[f'text_{lang}']}",
                                  callback_data=f"{button['data']}_{order_id}")]
            for button in buttons.values()
        ])

    @staticmethod
    def __get_paginate_keyboard(data, history=None):
        wanted, orders = data
        length = len(orders)
        state = 'h_' if history else ''

        if wanted == 1 and length == 1:
            button1_text = '.'
            button1_data = 'dot_1'
            button3_text = '.'
            button3_data = 'dot_2'

        elif wanted == 1 and length > 1:
            button1_text = '.'
            button1_data = 'dot'
            button3_text = '⏩'
            button3_data = f'{state}w_{wanted + 1}'

        elif wanted == length:
            button1_text = '⏪'
            button1_data = f'{state}w_{wanted - 1}'
            button3_text = '.'
            button3_data = 'dot'

        else:
            button1_text = '⏪'
            button1_data = f'{state}w_{wanted - 1}'
            button3_text = '⏩'
            button3_data = f'{state}w_{wanted + 1}'

        button2_text = f'{wanted}/{length}'
        button2_data = 'None'

        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(button1_text, callback_data=button1_data),
                InlineKeyboardButton(button2_text, callback_data=button2_data),
                InlineKeyboardButton(button3_text, callback_data=button3_data),
            ],
        ])

    @staticmethod
    def __get_edit_books_keyboard(buttons, lang, data):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{item['emoji']} {item[f'text_{lang}']}", callback_data='add_book')]
            if TITLE not in item else [InlineKeyboardButton(f"📝 {item[TITLE]}", callback_data=f'edit_book_{item[ID]}')]
            for item in list(buttons.values()) + data
        ])

    @staticmethod
    def __get_edit_book_keyboard(buttons, lang, data):
        inline_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{button['emoji']} {button[f'text_{lang}']}", callback_data=button['data'])]
            for button in buttons.values()
        ])
        if data['description_url']:
            emoji = inline_keyboard_types[book_keyboard]['about_book_btn']["emoji"]
            inline_keyboard.inline_keyboard.insert(0, [
                InlineKeyboardButton(f'{emoji} {inline_keyboard_types[book_keyboard]["about_book_btn"]["text_uz"]}',
                                     url=data['description_url'])
            ])
        return inline_keyboard

    def get_markup(self):
        return self.__keyboard
