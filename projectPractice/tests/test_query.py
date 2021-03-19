import unittest
from projectPractice import db_connect, Table, db_disconnect




class TestQuery(unittest.TestCase):
    def test_create_simple_table(self):
        db_connect('PostgreSQL ODBC Driver(UNICODE)', '127.0.0.1', '5432', 'postgres', user='postgres', password='abc123', autocomm=True)
        test_table = Table('test_table')
        test_table.integer('int_field')
        test_table.string('str_field', 120)
        test_table.create_table()

        test_table_created = Table('test_table')
        test_table_created.drop()

        db_disconnect()

    def test_create_table_with_modif(self):
        db_connect('PostgreSQL ODBC Driver(UNICODE)', '127.0.0.1', '5432', 'postgres', user='postgres',
                   password='abc123', autocomm=True)
        test_table = Table('test_table')
        test_table.id()
        test_table.integer('int_field').unique()
        test_table.string('str_field', 120).default('default_value')
        test_table.bool('bool_field').nullable(False)
        test_table.integer('autoincr_field').autoincrement()
        test_table.create_table()

        test_table_created = Table('test_table')
        test_table_created.drop()

        db_disconnect()

    def test_create_table_with_fk(self):
        pass


if __name__ == '__main__':
    unittest.main()