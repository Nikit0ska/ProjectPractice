import threading

from projectPractice.Connector import Connector
from projectPractice.ConnThread import ConnThread
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
def db_read_table(table_name):
    conn = __get_conn_thread().connector
    conn.execute(f"SELECT * FROM {table_name};")
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
    return 1


@errors.err_decor
def db_drop(db_name):
    conn = __get_conn_thread().connector
    conn.execute(f"DROP DATABASE {db_name};")
    return 1

