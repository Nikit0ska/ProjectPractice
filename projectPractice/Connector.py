import pyodbc
import threading


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


class ConnThread(threading.Thread):
    def __init__(self, connector):
        for thread in threading.enumerate():
            if type(thread) == ConnThread:
                raise ConnectionError
        super().__init__(target=self.__inf, daemon=True)
        self.connector = connector

    def __inf(self):
        while True:
            if not self.connector.is_connected:
                break

    def stop_thread(self):
        self.connector.close_connection()
        self.join()


def db_connect(driver, server, port, db, user='', password=''):
    conn = Connector(driver, server, port, db, uid=user, pwd=password)
    thread = ConnThread(conn)
    thread.start()


def get_conn_thread():
    for thread in threading.enumerate():
        if type(thread) == ConnThread:
            return thread
    return None


def db_disconnect():
    conn_thread = get_conn_thread()
    conn_thread.stop_thread()
    return 'disconnection is successful'


def db_read_table(table_name):
    conn = get_conn_thread().connector
    conn.execute(f"SELECT * FROM {table_name};")
    return conn.cursor.fetchall()


def query_execute(query):
    conn = get_conn_thread().connector
    conn.execute(query)


# db_connect('PostgreSQL ANSI', 'localhost', 5432, 'postgres', user='postgres', password='abc123')
# print(threading.enumerate())
# db_disconnect()
# print(threading.enumerate())
# db_connect('PostgreSQL ANSI', 'localhost', 5432, 'postgres', user='postgres', password='abc123')
# print(threading.enumerate())
# query_execute("INSERT INTO test VALUES(3, 'test');")
# print(db_read_table('test'))
# db_disconnect()

