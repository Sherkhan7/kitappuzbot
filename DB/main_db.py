import pymysql.cursors
from contextlib import closing
from config import DB_CONFIG


def get_connection():
    connection = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        cursorclass=pymysql.cursors.DictCursor,
    )
    return connection


users_table_name = 'users'
books_table_name = 'books'


def insert_data(data, table_name):
    data_keys = tuple(data.keys())
    data_values = tuple(data.values())

    fields = ','.join(data_keys)
    mask = ','.join(['%s'] * len(data_values))

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            sql = f'INSERT INTO {table_name} ({fields}) VALUES ({mask})'

            cursor.execute(sql, data_values)
            connection.commit()

    value = cursor.lastrowid

    print(f'{table_name}: +{cursor.rowcount}(last_row_id = {value})')

    return value


def insert_order_items(items_data, table_name):
    basket = items_data.pop('basket')
    data_keys = list(items_data.keys())
    data_keys += ['book_id', 'quantity']
    data_values = tuple(items_data.values())

    data_values = [data_values + tuple([book_id, quantity]) for (book_id, quantity) in basket.items()]

    fields = ','.join(data_keys)
    mask = ','.join(['%s'] * len(data_keys))

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            sql = f'INSERT INTO {table_name} ({fields}) VALUES ({mask})'

            cursor.executemany(sql, data_values)
            connection.commit()

    value = cursor.rowcount

    print(f'{table_name}: +{value}')

    return value


def insert_order_items_2(data_values, fields_list, table_name):
    fields = ','.join(fields_list)
    mask = ','.join(['%s'] * len(fields_list))

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            sql = f'INSERT INTO {table_name} ({fields}) VALUES ({mask})'

            cursor.executemany(sql, data_values)
            connection.commit()

    print(f'{table_name}: +{cursor.rowcount}')

    return cursor.rowcount


def get_user(id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {users_table_name} WHERE tg_id = %s OR id = %s', (id, id))

    return cursor.fetchone()


def get_book(id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {books_table_name} WHERE id = %s', id)

    return cursor.fetchone()


def get_all_books():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {books_table_name}')

    return cursor.fetchall()


def get_all_users():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {users_table_name}')

    return cursor.fetchall()


def get_all_orders():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM `orders`')

    return cursor.fetchall()


def get_books(ids):
    interval = ",".join(ids)

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {books_table_name} WHERE id in ({interval}) ORDER BY id DESC')

    return cursor.fetchall()


def get_order_items_book_title(order_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT oi.*, b.title FROM `order_items` as oi INNER JOIN books as b ON oi.book_id=b.id '
                f'WHERE order_id = %s', order_id)
    return cursor.fetchall()


def get_user_orders(user_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT * FROM orders WHERE orders.user_id = %s ORDER BY id DESC', user_id)

    return cursor.fetchall()


def get_order(order_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT * FROM orders WHERE orders.id = %s', order_id)

    return cursor.fetchone()


def get_orders_by_status(status):
    if isinstance(status, tuple):
        sql = f'SELECT * FROM orders WHERE orders.status = %s OR orders.status = %s ORDER BY id DESC'
    else:
        sql = f'SELECT * FROM orders WHERE orders.status = %s ORDER BY id DESC'

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, status)

    return cursor.fetchall()


def update_order_status(status, order_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE orders SET status = %s WHERE id = %s', (status, order_id))
            connection.commit()

    return_value = 'not updated'

    if connection.affected_rows() != 0:
        return_value = 'updated'

    return return_value


def update_post_status(status, post_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute('UPDATE posts SET status = %s WHERE id = %s', (status, post_id))
            connection.commit()

    return_value = 'not updated'

    if connection.affected_rows() != 0:
        return_value = 'updated'

    return return_value


def update_user_info(id, **kwargs):
    if 'lang' in kwargs.keys():
        value = kwargs['lang']
        sql = f'UPDATE testdb.{users_table_name} SET lang = %s WHERE tg_id = %s OR id = %s'

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (value, id, id))
            connection.commit()

    return_value = 'not updated'

    if connection.affected_rows() != 0:
        return_value = 'updated'

    return return_value
