from DB import get_books_by_ids
from layouts.layoutdicts import *
from helpers import wrap_tags


def get_book_layout(book_data, lang):
    title = book_data[TITLE]
    price = f"{book_data[PRICE]:,} so'm".replace(',', ' ')
    year = f"📅 {BOOK_DICT[lang][YEAR_TEXT]}: {wrap_tags(book_data[YEAR], 'yil')}\n" if book_data[YEAR] else ''
    author = f'👤 {BOOK_DICT[lang][AUTHOR_TEXT]}: {wrap_tags(book_data[AUTHOR])}\n' if book_data[AUTHOR] else ''
    amount = f"🔢 {BOOK_DICT[lang][AMOUNT_TEXT]}: {wrap_tags(book_data[AMOUNT], 'bet')}\n" \
        if book_data[AMOUNT] else ''
    book_lang = f'🌏 {BOOK_DICT[lang][LANG_TEXT]}: {wrap_tags(book_data[LANG])}\n' if book_data[LANG] else ''
    translator = f'👤 {BOOK_DICT[lang][TRANSLATOR_TEXT]}: {wrap_tags(book_data[TRANSLATOR])}\n' \
        if book_data[TRANSLATOR] else ''
    cover_type = f'📗 {BOOK_DICT[lang][COVER_TYPE_TEXT]}: {wrap_tags(book_data[COVER_TYPE])}\n' \
        if book_data[COVER_TYPE] else ''

    return f'🏷 {BOOK_DICT[lang][TITLE_TEXT]}: {wrap_tags(title)}\n' \
           f'💸 {BOOK_DICT[lang][PRICE_TEXT]}: {wrap_tags(price)}\n' \
           f'{year}{book_lang}{author}{translator}{cover_type}{amount}' \
           f'🤖 @kitappuzbot ©'


def get_basket_layout(orders, lang, data=None):
    books_ids = [str(key) for key in orders.keys()]
    books = get_books_by_ids(books_ids)
    if books:
        layout = ''
        total = 0
        for index, book in enumerate(books):
            total += book[PRICE] * orders[book[ID]]
            quantity_and_price = f"{orders[book[ID]]} X {book[PRICE]:,} so'm".replace(',', ' ')
            layout += f'{index + 1}) 📕 {wrap_tags(book[TITLE])}:\n' \
                      f'{quantity_and_price}\n' \
                      f'{"_" * 22}\n\n'
        data = data if data else '🛒 Savat'
        layout = wrap_tags(data) + "\n\n" + layout
        layout += f"Jami: {total:,} so'm\n".replace(',', ' ')
        return layout


def get_books_layout(order, order_items, client, data):
    books_text = ''
    username_text = f'Telegram: {wrap_tags("@" + client[USERNAME])}\n\n' if client[USERNAME] else '\n'

    for index, item in enumerate(order_items):
        books_text += f'{index + 1}) Kitob nomi: {wrap_tags(item[TITLE])}\n' \
                      f'Soni: {wrap_tags(item["quantity"], "ta")}\n' \
                      f'{"_" * 22}\n'
    client_text = f'🆔 {order_items[0]["order_id"]} {data["label"]}\n\n' \
                  f'Status: {wrap_tags(data[STATUS])}\n' \
                  f'Yaratilgan vaqti: {wrap_tags(order["created_at"].strftime("%d-%m-%Y %X"))}\n\n' \
                  f'Ism: {wrap_tags(client[FULLNAME])}\n' \
                  f'Tel: {wrap_tags(order[PHONE_NUMBER])}\n' \
                  f'{username_text}'
    return client_text + books_text


# def get_user_info_layout(user):
#     layout = f"{USER_INFO_LAYOUT_DICT[user['lang']][NAME]}: {wrap_tags(user['name'])}\n\n" \
#              f"{USER_INFO_LAYOUT_DICT[user['lang']][SURNAME]}: {wrap_tags(user['surname'])}"
# f"<b><i>{'-'.ljust(30, '-')}</i></b> \n" \
# f"<b>\u0000260e {phone}: <i><u>{format_phone_number(user['phone_number'])}</u></i></b>" \
# f"<b><i>\u0000260e {phone_2}: </i><u>{user['phone_number2']}</u></b> \n"

# return layout


def get_phone_number_layout(lang):
    return f"{PHONE_NUMBER_LAYOUT_DICT[lang][1]}:\n\n" \
           f"{PHONE_NUMBER_LAYOUT_DICT[lang][2]}: {wrap_tags('XX XXXXXXX')}\n" \
           f"{PHONE_NUMBER_LAYOUT_DICT[lang][3]}\n" \
           f"{PHONE_NUMBER_LAYOUT_DICT[lang][2]}: {wrap_tags('+998 XX XXXXXXX')}\n"
