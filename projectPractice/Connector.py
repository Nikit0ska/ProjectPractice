import pyodbc
import threading
import time


# Для MongoDB: https://www.cdata.com/drivers/mongodb/download/odbc/
# Для PosgreSQL: https://ftp.postgresql.org/pub/odbc/versions/msi/psqlodbc_12_02_0000.zip
# Посмотреть установленные драйвера: pyodbc.drivers()

class Connector:
    def __init__(self, driver, server, port, database, uid=str(), pwd=str(), autocommit=True):
        self.connection = pyodbc.connect(
            f'DRIVER={{{driver}}};SERVER={server};PORT={port};DATABASE={database};UID={uid}'
            f';PWD={pwd};')

        self.cursor = self.connection.cursor()
        self.connection.autocommit = autocommit
        self.is_connected = True

    def new_connect(self, driver, server, port, database, uid=str(), pwd=str(), autocommit=True):
        self.connection = pyodbc.connect(
            f'DRIVER={{{driver}}};SERVER={server};PORT={port};DATABASE={database};UID={uid}'
            f';PWD={pwd};')
        self.cursor = self.connection.cursor()
        self.connection.autocommit = autocommit
        self.is_connected = True

    def execute(self, query):
        self.cursor = self.connection.execute(query)
        return self.cursor

    def close_connection(self):
        self.connection.close()
        self.is_connected = False
        self.connection = None


def db_connect(driver, server, port, db, user='', password=''):
    flag = True
    for thread in threading.enumerate():
        if thread.name == ('DB_CONNECTOR' + str(thread.ident)):
            if not thread.connector.is_connected:
                thread.connector = Connector(driver, server, port, db, uid=user, pwd=password)
                flag = False
            else:
                raise ConnectionError
    if flag:
        conn_thread = threading.Thread(target=inf, daemon=True)
        conn_thread.connector = Connector(driver, server, port, db, uid=user, pwd=password)
        conn_thread.start()
        conn_thread.setName('DB_CONNECTOR' + str(conn_thread.ident))
        return "connection is successful"


def inf():
    while True:
        pass


def get_conn_thread():
    for thread in threading.enumerate():
        if thread.name == 'DB_CONNECTOR' + str(thread.ident):
            if thread.connector.is_connected:
                return thread
            else:
                raise ConnectionError


def db_disconnect():
    thread = get_conn_thread()
    thread.connector.close_connection()
    return 'disconnection is successful'


def db_read_table(table_name):
    conn = get_conn_thread().connector
    conn.execute(f"SELECT * FROM {table_name};")
    return conn.cursor.fetchall()


# print(pyodbc.drivers())
# db_connect('PostgreSQL ODBC Driver(ANSI)', 'localhost', 5432, 'postgres', user='postgres', password='abc123')
# print(db_read_table('test'))
# db_disconnect()