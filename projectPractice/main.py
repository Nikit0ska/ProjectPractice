from projectPractice import db_funcs
from projectPractice.Table import *
import pyodbc



print(pyodbc.drivers())


db_funcs.db_connect('Devart ODBC Driver for MongoDB', '127.0.0.1', '27017', 'nikit0ska', autocomm=True)

table = Table('test')
table.string('name', 255)
table.integer('age')
table.string('description', 255)
table.create_table()

table = Table('test')
print(table.get_form_data())
print()
table.insert(name='test1', age=1)
table.insert(name='test2', age=2, description="asdwadwadwqewqhqhehhqwhequhhu`12317")
print(table.get_form_data())
print()
table.where('age', '=', '1')
table.update(description='new description')
table.clear_selected_data()
print(table.get_form_data())
print()
table.where('age', '=', '2')
table.delete()
print(table.get_form_data())

db_funcs.import_csv_db("csv", 'cities.csv')


