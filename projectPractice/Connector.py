import pyodbc
import projectPractice.errors


class Connector:
    def __init__(self, driver, server, port, database, uid=str(), pwd=str(), autocommit=True):
        try:
            self.connection = pyodbc.connect(
                f'DRIVER={{{driver}}};SERVER={server};PORT={port};DATABASE={database};UID={uid}'
                f';PWD={pwd};')
        except pyodbc.Error as ex:
            sqlstate = ex.args[1]
            raise projectPractice.errors.OdbcConnectionError(sqlstate) from None
        self.cursor = self.connection.cursor()
        self.connection.autocommit = autocommit
        self.is_connected = True
        self.con_params = {'driver': driver, 'server': server, 'port': port, 'database': database, 'user': uid,
                           'password': pwd, 'autocommit': autocommit}

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
