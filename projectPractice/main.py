from projectPractice import db_funcs
from projectPractice.Table import Table
import pyodbc


print(pyodbc.drivers())

db_funcs.db_connect('PostgreSQL Unicode', 'localhost', 5432, 'nikit0ska', user='nikit0ska', password='abc123', autocomm=True)
table = Table('test')
# print(table.columns)

# table.id()
# table.string('username', 100)
# table.integer('age')
# query = table.create_table()
# db_funcs.db_execute_query(query)


