from projectPractice import db_funcs, Table
import timeit
db_funcs.db_connect('PostgreSQL Unicode', '127.0.0.1', '5432', 'nikit0ska', user='nikit0ska', password='abc123', autocomm=True)
print(timeit.timeit("""
from projectPractice import db_funcs, Table

db_funcs.import_csv_db('xl_table', 'cities.csv')
db_funcs.db_execute_query('DROP TABLE xl_table')
""", number=100))

# from projectPractice import Table, db_funcs, get_cursor
# import pyodbc
# db_funcs.db_connect('PostgreSQL Unicode', '127.0.0.1', '5432', 'nikit0ska', user='nikit0ska', password='abc123', autocomm=True)
#



