import pymysql.cursors
from contextlib import closing
from config import DB_CONFIG, DEVELOPER_CHAT_ID


def get_connection():
    return pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        cursorclass=pymysql.cursors.DictCursor,
    )


def insert_data(data, table_name):
    data_keys = tuple(data.keys())
    data_values = tuple(data.values())
    fields = ','.join(data_keys)
    placeholder = ','.join(['%s'] * len(data_values))
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            sql = f'INSERT INTO {table_name} ({fields}) VALUES ({placeholder})'
            cursor.execute(sql, data_values)
            connection.commit()
    print(f'{table_name}: +{cursor.rowcount}(last_row_id = {cursor.lastrowid})')
    return cursor.lastrowid


def insert_order_items(data_values, fields_list, table_name):
    fields = ','.join(fields_list)
    placeholder = ','.join(['%s'] * len(fields_list))
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            sql = f'INSERT INTO {table_name} ({fields}) VALUES ({placeholder})'
            cursor.executemany(sql, data_values)
            connection.commit()
    print(f'{table_name}: +{cursor.rowcount}')
    return cursor.rowcount


def get_user(_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE tg_id = %s OR id = %s', (_id, _id))
    return cursor.fetchone()


def get_book(_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM books WHERE id = %s AND is_removed = FALSE', _id)
    return cursor.fetchone()


def get_book_data(_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM books WHERE id = %s', _id)
    return cursor.fetchone()


def delete_book(_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE books SET is_removed = TRUE WHERE id = %s', _id)
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def delete_action(_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE actions SET is_active = FALSE WHERE id = %s', _id)
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def get_all_books():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM books WHERE is_removed = FALSE')
    return cursor.fetchall()


def get_all_actions():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM actions WHERE is_active = TRUE')
    return cursor.fetchall()


def get_action(_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM actions WHERE id = %s and is_active = TRUE', _id)
    return cursor.fetchone()


def get_action_data(_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM actions WHERE id = %s', _id)
    return cursor.fetchone()


def get_all_admins():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM users WHERE is_admin = TRUE AND tg_id != {DEVELOPER_CHAT_ID}')
    return cursor.fetchall()


def get_all_users():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users')
    return cursor.fetchall()


def get_all_orders():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM orders')
    return cursor.fetchall()


def get_books_by_ids(ids):
    placeholder = ",".join(['%s'] * len(ids))
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            sql = f'SELECT * FROM books WHERE id IN ({placeholder}) AND is_removed = FALSE ORDER BY id DESC'
            cursor.execute(sql, ids)
    return cursor.fetchall()


def get_user_by_username(username):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE username = %s', username)
    return cursor.fetchone()


def get_order_items_book_title(order_id):
    sql = 'SELECT oi.*, b.title FROM order_items as oi INNER JOIN books as b ON oi.book_id=b.id WHERE order_id = %s'
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, order_id)
    return cursor.fetchall()


def get_contact_us_text():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM contact_us_text')
    return cursor.fetchone()


def get_user_orders(user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM orders WHERE user_id = %s ORDER BY id DESC', user_id)
    return cursor.fetchall()


def get_order(order_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM orders WHERE orders.id = %s', order_id)
    return cursor.fetchone()


def get_orders_by_status(*args):
    placeholder = ','.join(['%s'] * len(args))
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            sql = f'SELECT * FROM orders WHERE status IN ({placeholder}) ORDER BY id DESC'
            cursor.execute(sql, args)
    return cursor.fetchall()


def update_order_status(status, order_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE orders SET status = %s WHERE id = %s', (status, order_id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_contact_us_text(text):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE contact_us_text SET text = %s ', text)
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_post_status(status, post_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE posts SET status = %s WHERE id = %s', (status, post_id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_user_isadmin(is_admin, _id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE users SET is_admin = %s WHERE tg_id = %s', (is_admin, _id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_book_photo(file_id, _id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE books SET photo = %s WHERE id = %s', (file_id, _id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_book_title(title, _id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE books SET title = %s WHERE id = %s', (title, _id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_book_price(price, _id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE books SET price = %s WHERE id = %s', (price, _id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_book_lang(lang, _id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE books SET lang = %s WHERE id = %s', (lang, _id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_book_translator(translator, _id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE books SET translator = %s WHERE id = %s', (translator, _id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_book_cover(cover_type, _id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE books SET cover_type = %s WHERE id = %s', (cover_type, _id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_book_url(description_url, _id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE books SET description_url = %s WHERE id = %s', (description_url, _id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_book_amount(amount, _id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE books SET amount = %s WHERE id = %s', (amount, _id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_book_year(year, _id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE books SET year = %s WHERE id = %s', (year, _id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'


def update_book_author(author, _id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE books SET author = %s WHERE id = %s', (author, _id))
            connection.commit()
    return 'updated' if connection.affected_rows() != 0 else 'not updated'
