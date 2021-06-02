from telegram import ReplyKeyboardMarkup, KeyboardButton
from replykeyboards.replykeyboardtypes import *


class ReplyKeyboard(object):

    def __init__(self, keyb_type, lang):

        self.__type = keyb_type
        self.__lang = lang

        self.__keyboard = self.__create_reply_keyboard(self.__type, self.__lang)

    def __create_reply_keyboard(self, keyb_type, lang):

        if keyb_type == client_menu_keyboard or keyb_type == admin_menu_keyboard:
            return self.__get_menu_keyboard(reply_keyboard_types[keyb_type][lang], keyb_type)

        elif keyb_type == settings_keyboard:

            return self.__get_settings_keyboard(reply_keyboard_types[keyb_type][lang])

        elif keyb_type == phone_number_keyboard:
            return self.__get_phone_number_keyboard(reply_keyboard_types[keyb_type][lang])

        elif keyb_type == location_keyboard:
            return self.__get_location_keyboard(reply_keyboard_types[keyb_type][lang])

    @staticmethod
    def __get_menu_keyboard(buttons, keyb_type):
        emoji_1 = '📚'
        emoji_2 = '📄'
        emoji_3 = '☎️'
        if keyb_type == admin_menu_keyboard:
            emoji_1 = '📒'
            emoji_2 = '📑'
            emoji_3 = '🗄'
            emoji_4 = '💾'

        reply_keyboard = ReplyKeyboardMarkup([
            [KeyboardButton(f'{emoji_1} {buttons[1]}')],
            [KeyboardButton(f'{emoji_2} {buttons[2]}')],
            [KeyboardButton(f'{emoji_3} {buttons[3]}')],
        ], resize_keyboard=True)
        if keyb_type == client_menu_keyboard:
            reply_keyboard.keyboard.insert(0, [KeyboardButton(buttons[5])])
        elif keyb_type == admin_menu_keyboard:
            reply_keyboard.keyboard.append([KeyboardButton(f'{emoji_4} {buttons[4]}')])

        return reply_keyboard

    @staticmethod
    def __get_settings_keyboard(button):

        return ReplyKeyboardMarkup([

            [KeyboardButton(f'\U0001F4D4 {button[1]}')],
            [KeyboardButton(f'\U0001F310 {button[2]}')],
            [KeyboardButton(f'\U00002B05 {button[3]}')],

        ], resize_keyboard=True)

    @staticmethod
    def __get_phone_number_keyboard(buttons):

        return ReplyKeyboardMarkup([
            [
                KeyboardButton(f'\U0001F464 {buttons[1]}', request_contact=True)]
        ], resize_keyboard=True)

    @staticmethod
    def __get_location_keyboard(buttons):

        return ReplyKeyboardMarkup([

            [KeyboardButton(f'{buttons[1]}')],
            [KeyboardButton(f'\U0001F4CD {buttons[2]}', request_location=True)],

        ], resize_keyboard=True)

    def get_keyboard(self):
        return self.__keyboard
