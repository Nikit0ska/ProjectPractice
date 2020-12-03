import threading

from projectPractice.Connector import Connector
from projectPractice.ConnThread import ConnThread
from projectPractice.Table import *
import projectPractice.errors as errors


# Для MongoDB: https://www.cdata.com/drivers/mongodb/download/odbc/
# Для PosgreSQL: https://ftp.postgresql.org/pub/odbc/versions/msi/psqlodbc_12_02_0000.zip
# Посмотреть установленные драйвера: pyodbc.drivers()


def db_connect(driver, server, port, db, user='', password='', autocomm=True):
    conn = Connector(driver, server, port, db, uid=user, pwd=password, autocommit=autocomm)
    thread = ConnThread(conn)
    thread.start()


def __get_conn_thread():
    con_thread = None
    for thread in threading.enumerate():
        if type(thread) == ConnThread:
            con_thread = thread
            return con_thread
    if con_thread is None:
        raise errors.OdbcConnectionError('No connection')


@errors.err_decor
def db_disconnect():
    conn_thread = __get_conn_thread()
    conn_thread.stop_thread()
    return None


@errors.err_decor
def db_read_table(table, limit=0, sql_condition='', order_by=('', '')):
    conn = __get_conn_thread().connector
    if type(table) == CreatedTable:
        return table.get_data()
    query = f'SELECT * FROM {table}'
    if sql_condition != '':
        query += f" where {sql_condition}"
    if order_by != ('', ''):
        query += f" order by {order_by[0]} {order_by[1]}"
    if limit != 0:
        query += f" limit {limit}"
    query += ';'
    conn.execute(query)
    return conn.cursor.fetchall()


@errors.err_decor
def db_execute_query(query):
    conn = __get_conn_thread().connector
    if 'select' in query.lower():
        content = conn.execute(query)
        return content.fetchall()
    else:
        conn.execute(query)
        return 1


@errors.err_decor
def db_create(db_name):
    conn = __get_conn_thread().connector
    conn.execute(f"CREATE DATABASE {db_name};")
    return True


@errors.err_decor
def db_drop(db_name):
    conn = __get_conn_thread().connector
    conn.execute(f"DROP DATABASE {db_name};")
    return True


@errors.err_decor
def db_change(db_name):
    conn = __get_conn_thread().connector
    params = conn.con_params
    db_disconnect()
    db_connect(params['driver'], params['server'], params['port'], db_name, params['user'], params['password'],
               params['autocommit'])
