import pymysql.cursors
from contextlib import closing
import json
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

    print(f'{table_name}: +1(last_row_id = {value})')
    return value


def insert_order_items(items_data, table_name):
    basket = items_data.pop('basket')
    items_data['geolocation'] = json.dumps(items_data['geolocation']) if items_data['geolocation'] else None
    data_keys = list(items_data.keys())
    data_keys += ['book_id', 'quantity']
    data_values = tuple(items_data.values())

    data_values = [data_values + tuple([book_id, quantity['quantity']]) for (book_id, quantity) in basket.items()]

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


def get_user(id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {users_table_name} WHERE tg_id = %s OR id = %s', (id, id))
            record = cursor.fetchone()

    return record


def get_book(id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {books_table_name} WHERE id = %s', id)
            record = cursor.fetchone()

    return record


def get_all_books():
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {books_table_name}')
            record = cursor.fetchall()

    return record


def get_books(ids):
    interval = ",".join(ids)

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM {books_table_name} WHERE id in ({interval})')
            record = cursor.fetchall()

    return record


def get_order_items(order_id):
    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f'SELECT * FROM order_items LEFT JOIN orders ON order_items.order_id = orders.id WHERE '
                f'order_items.order_id= %s', order_id)

            record = cursor.fetchone()

    return record


def update_order_status(statsus, order_id):
    sql = f'UPDATE orders SET status = %s WHERE id = %s'

    with closing(get_connection()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, (statsus, order_id))
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
