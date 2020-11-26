from projectPractice import db_funcs
from projectPractice.Table import *
import pyodbc


print(pyodbc.drivers())

db_funcs.db_connect('PostgreSQL Unicode', 'localhost', 5432, 'nikit0ska', user='nikit0ska', password='abc123', autocomm=True)

a = Table('test')
if type(a) == NewTable:
    a.id()
    a.string('username', 20)
    a.integer('age').default(0)
    a.create_table()
else:
    a.insert({'username': 'w', 'age': '22'})
    print(a.get_form_data())



