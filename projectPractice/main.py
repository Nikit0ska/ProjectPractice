from projectPractice import db_funcs
import pyodbc


print(pyodbc.drivers())

db_funcs.db_connect('PostgreSQL Unicode', 'localhost', 5432, 'nikit0ska', user='nikit0ska', password='abc123', autocomm=True)
a = db_funcs.db_execute_query('SELECT * FROM test')
print(len(a))
