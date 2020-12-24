from projectPractice import db_funcs
from projectPractice.Table import *
import pyodbc


print(pyodbc.drivers())

db_funcs.db_connect('PostgreSQL Unicode', 'localhost', 5432, 'nikit0ska', user='nikit0ska', password='abc123', autocomm=True)
# db_funcs.import_csv_db('csv_table','cities.csv')
# db_funcs.import_xl_db('test', 'Financial Sample.xlsx')

