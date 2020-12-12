from helpers import wrap_tags
from layouts.layoutdicts import *
from DB import get_books


def get_book_layout(book_data, user_lang):
    title = book_data[TITLE]
    author = book_data[AUTHOR]
    amount = str(book_data[AMOUNT]) + " bet"
    lang = book_data[LANG]
    translator = str(book_data[TRANSLATOR])
    cover_type = book_data[COVER_TYPE]
    price = str(book_data[PRICE]) + " so'm"
    year = str(book_data[YEAR])

    layout = [
        f'\U0001F3F7	 {BOOK_DICT[user_lang][TITLE_TEXT]}: {wrap_tags(title)}',
        f'\U0001F464   {BOOK_DICT[user_lang][AUTHOR_TEXT]}: {wrap_tags(author)}',
        f'\U0001F3E2   {BOOK_DICT[user_lang][AMOUNT_TEXT]}: {wrap_tags(amount)}',
        f'\U0001F30F	 {BOOK_DICT[user_lang][LANG_TEXT]}: {wrap_tags(lang)}',
        f'\U0001F464   {BOOK_DICT[user_lang][TRANSLATOR_TEXT]}: {wrap_tags(translator)}',
        f'\U0001F4D5   {BOOK_DICT[user_lang][COVER_TYPE_TEXT]}: {wrap_tags(cover_type)}',
        f'\U0001F4C5   {BOOK_DICT[user_lang][YEAR_TEXT]}: {wrap_tags(year)}',
        f'\U0001F4B0   {BOOK_DICT[user_lang][PRICE_TEXT]}: {wrap_tags(price)}\n',
        f'\U0001F916   @kitappuzbot \U000000A9',
    ]

    if not translator:
        layout.pop(4)

    return '\n'.join(layout)


def get_basket_layout(orders, lang, data=None):
    books_ids = [str(key) for key in orders.keys()]
    books = get_books(books_ids)

    layout = ''
    total = 0

    for book in books:
        total += book['price'] * orders[book["id"]]["quantity"]
        quantity_price = str(orders[book["id"]]["quantity"]) + " X " + str(book["price"]) + " so'm"

        layout += f'\U0001F4D5 {wrap_tags(book["title"])}:\n' \
                  f'{quantity_price}' \
                  f'\n----------------------\n'

    data = data if data else 'Savat'

    layout = wrap_tags(data) + "\n\n" + layout
    layout += f"Jami: {total} so'm\n\n"

    return layout


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
