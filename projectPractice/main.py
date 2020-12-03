from projectPractice import db_funcs
from projectPractice.Table import *
import pyodbc


print(pyodbc.drivers())

db_funcs.db_connect('PostgreSQL Unicode', 'localhost', 5432, 'nikit0ska', user='nikit0ska', password='abc123', autocomm=True)
b = Table('test1')

b.integer('foreign_field', is_foreign=True).constraint('some_cons').on_delete(set_null=True).references('some_table', 'some_field')

b.create_table()
