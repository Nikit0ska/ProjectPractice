from projectPractice import db_funcs
from projectPractice.Table import *
import pyodbc
# import time


print(pyodbc.drivers())

# start_time = time.time()
db_funcs.db_connect('PostgreSQL Unicode', 'localhost', 5432, 'nikit0ska', user='nikit0ska', password='abc123', autocomm=True)
# db_funcs.import_csv_db('csv_table','Financial Sample.csv', delimiter=";")
db_funcs.import_xl_db('test', 'Financial Sample.xlsx')
# print("--- %s seconds ---" % (time.time() - start_time))

