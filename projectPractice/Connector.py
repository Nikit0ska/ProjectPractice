import pyodbc

# Для MongoDB: https://www.cdata.com/drivers/mongodb/download/odbc/
# Для PosgreSQL: https://ftp.postgresql.org/pub/odbc/versions/msi/psqlodbc_12_02_0000.zip
# Посмотреть установленные драйвера: pyodbc.drivers()

class Connector:
    def __init__(self, driver, server, port, database, uid=str(), pwd=str(), autocommit=True):

        self.connection = pyodbc.connect(f'DRIVER={{{driver}}};SERVER={server};PORT={port};DATABASE={database};UID={uid}'
                                             f';PWD={pwd};')

        self.cursor = self.connection.cursor()
        self.connection.autocommit = autocommit

    def execute(self, query):
        self.cursor = self.connection.execute(query)
        return self.cursor

