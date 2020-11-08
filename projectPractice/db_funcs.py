import threading

from projectPractice.Connector import Connector
from projectPractice.ConnThread import ConnThread


# Для MongoDB: https://www.cdata.com/drivers/mongodb/download/odbc/
# Для PosgreSQL: https://ftp.postgresql.org/pub/odbc/versions/msi/psqlodbc_12_02_0000.zip
# Посмотреть установленные драйвера: pyodbc.drivers()

def db_connect(driver, server, port, db, user='', password=''):
    conn = Connector(driver, server, port, db, uid=user, pwd=password)
    thread = ConnThread(conn)
    thread.start()


def __get_conn_thread():
    for thread in threading.enumerate():
        if type(thread) == ConnThread:
            return thread
    return None


def db_disconnect():
    conn_thread = __get_conn_thread()
    conn_thread.stop_thread()
    return 'disconnection is successful'


def db_read_table(table_name):
    conn = __get_conn_thread().connector
    conn.execute(f"SELECT * FROM {table_name};")
    return conn.cursor.fetchall()


def db_execute_query(query):
    if __get_conn_thread() is not None:
        conn = __get_conn_thread().connector
        conn.execute(query)
    else:
        return "Can't find connection"


# db_connect('PostgreSQL ANSI', 'localhost', 5432, 'postgres', user='postgres', password='abc123')
# print(threading.enumerate())
# db_disconnect()
# print(threading.enumerate())
# db_connect('PostgreSQL ANSI', 'localhost', 5432, 'postgres', user='postgres', password='abc123')
# print(threading.enumerate())
# query_execute("INSERT INTO test VALUES(3, 'test');")
# print(db_read_table('test'))
# db_disconnect()
