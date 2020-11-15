from projectPractice import db_funcs
import pyodbc


print(pyodbc.drivers())

db_funcs.db_connect('PostgreSQL ANSI', 'localhost', 5432, 'nikit0ska', user='nikit0ska')
db_funcs.db_disconnect()
