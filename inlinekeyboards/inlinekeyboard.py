from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from DB import get_book, get_all_books
from inlinekeyboards.inlinekeyboardtypes import *
from globalvariables import *


class InlineKeyboard(object):
    def __init__(self, keyb_type, lang=None, data=None, history=None):

        self.__type = keyb_type
        self.__lang = lang
        self.__data = data
        self.__history = history
        self.__keyboard = self.__create_inline_keyboard(self.__type, self.__lang, self.__data, self.__history)

    def __create_inline_keyboard(self, keyb_type, lang, data, history):

        if keyb_type == books_keyboard:

            return self.__get_books_keyboard(data)

        elif keyb_type == book_keyboard:

            return self.__get_book_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == order_keyboard:

            return self.__get_order_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == basket_keyboard:

            return self.__get_basket_keyboard(inline_keyboard_types[keyb_type][lang])

        elif keyb_type == confirm_keyboard:

            return self.__get_confirm_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == orders_keyboard:

            return self.__get_orders_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == choose_keyboard:

            return self.__get_choose_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == delivery_keyboard:

            return self.__get_delivery_keyboard(inline_keyboard_types[keyb_type][lang], data)

        elif keyb_type == paginate_keyboard:

            return self.__get_paginate_keyboard(data, history)

        elif keyb_type == geo_keyboard:

            return self.__get_geo_keyboard(data)

    @staticmethod
    def __get_books_keyboard(data):

        inline_keyboard = [
            [InlineKeyboardButton(f'{book["title"]}', callback_data=f'book_{book["id"]}')]
            for book in get_all_books()
        ]

        if data:
            inline_keyboard.append([InlineKeyboardButton('savat', callback_data='basket')])

        return InlineKeyboardMarkup(inline_keyboard)

    @staticmethod
    def __get_book_keyboard(buttons, book_data):

        inline_keyboard = [
            [InlineKeyboardButton(buttons[2], callback_data=f'ordering')],
            [InlineKeyboardButton(buttons[3], callback_data='back')],
        ]

        if book_data['description_url']:
            inline_keyboard.insert(0, [InlineKeyboardButton(buttons[1], url=book_data['description_url'])])

        return InlineKeyboardMarkup(inline_keyboard)

    @staticmethod
    def __get_order_keyboard(buttons, book_id):

        button1_data = f'order_{book_id}'
        button2_data = 'back'

        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('-', callback_data='-'),
                    InlineKeyboardButton('1', callback_data='1'),
                    InlineKeyboardButton('+', callback_data='+'),
                ],

                [InlineKeyboardButton(buttons[1], callback_data=button1_data)],

                [InlineKeyboardButton(buttons[2], callback_data=button2_data)],
            ]
        )

    @staticmethod
    def __get_basket_keyboard(buttons):

        return InlineKeyboardMarkup([

            [InlineKeyboardButton(buttons[1], callback_data='continue')],
            [InlineKeyboardButton(buttons[2], callback_data='confirmation')]
        ])

    @staticmethod
    def __get_confirm_keyboard(buttons, data):

        inline_keyboard = []
        button1_text = 'Geolokatsiyam'
        button1_text = f'\U0001F4CD {button1_text}'
        # button2_text = f'\U0001F3C1 {button2_text}'

        if data:
            from_latitude = data['latitude']
            from_longitude = data['longitude']
            inline_keyboard.append(
                [InlineKeyboardButton(button1_text,
                                      url=f'http://www.google.com/maps/place/{from_latitude},{from_longitude}/'
                                          f'@{from_latitude},{from_longitude},12z')])

        button2_text = f'\U00002705 {buttons[0]}'
        button3_text = f'\U0000274C {buttons[1]}'

        inline_keyboard.extend([
            [InlineKeyboardButton(button2_text, callback_data='confirm')],
            [InlineKeyboardButton(button3_text, callback_data='cancel')]
        ])

        return InlineKeyboardMarkup(inline_keyboard)

    @staticmethod
    def __get_orders_keyboard(buttons, data):

        inline_keyboard = []
        button2_text = "Manzilni xaritadan ko'rish"
        # button1_text = f'\U0001F4CD {button1_text}'
        button2_text = f'\U0001F3C1 {button2_text}'

        if data[0]:
            from_latitude = data[0]['latitude']
            from_longitude = data[0]['longitude']
            inline_keyboard.append(
                [InlineKeyboardButton(button2_text,
                                      url=f'http://www.google.com/maps/place/{from_latitude},{from_longitude}/'
                                          f'@{from_latitude},{from_longitude},12z')])

        button2_text = f'\U00002705 {buttons[1]}'
        button3_text = f'\U0000274C {buttons[2]}'

        inline_keyboard.extend([
            [InlineKeyboardButton(button2_text, callback_data=f'r_{data[-1]}')],
            [InlineKeyboardButton(button3_text, callback_data=f'c_{data[-1]}')]
        ])

        return InlineKeyboardMarkup(inline_keyboard)

    @staticmethod
    def __get_geo_keyboard(data):
        button2_text = "Manzilni xaritadan ko'rish"
        # button1_text = f'\U0001F4CD {button1_text}'
        button2_text = f'\U0001F3C1 {button2_text}'

        from_latitude = data['latitude']
        from_longitude = data['longitude']

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(button2_text,
                                  url=f'http://www.google.com/maps/place/{from_latitude},{from_longitude}/'
                                      f'@{from_latitude},{from_longitude},12z')]
        ])

    @staticmethod
    def __get_choose_keyboard(buttons, data):

        return InlineKeyboardMarkup([

            [
                InlineKeyboardButton(buttons[1], callback_data=f'{data[0]}_y_{data[-1]}'),
                InlineKeyboardButton(buttons[2], callback_data=f'{data[0]}_n_{data[-1]}')
            ],
        ])

    @staticmethod
    def __get_delivery_keyboard(buttons, data):

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(buttons[0], callback_data=f'd_{data}')],
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

            button3_text = '\U000023E9'
            button3_data = f'{state}w_{wanted + 1}'

        elif wanted == length:
            button1_text = '\U000023EA'
            button1_data = f'{state}w_{wanted - 1}'

            button3_text = '.'
            button3_data = 'dot'

        else:
            button1_text = '\U000023EA'
            button1_data = f'{state}w_{wanted - 1}'

            button3_text = '\U000023E9'
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

    def get_keyboard(self):

        return self.__keyboard
