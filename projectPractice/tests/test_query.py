import unittest
from projectPractice import db_connect, Table, db_disconnect


class TestQuery(unittest.TestCase):
    def test_create_simple_table(self):
        db_connect('PostgreSQL ODBC Driver(UNICODE)', '127.0.0.1', '5432', 'postgres', user='postgres', password='abc123', autocomm=True)
        test_table = Table('test_table')
        test_table.integer('int_field')
        test_table.string('str_field', 120)
        struct = test_table.create_table()
        self.assertTable('test_table', struct)
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

        struct = test_table.create_table()

        self.assertTable('test_table', struct)

        test_table_created = Table('test_table')
        test_table_created.drop()

        db_disconnect()

    def test_create_table_with_fk(self):
        pass

    def assertTable(self, table_name, table_dict):
        created_table = Table(table_name)
        created_table_dict = created_table.columns
        # print(created_table_dict)
        # print(table_dict)
        for elem in created_table_dict:
            assert elem in table_dict
            if table_dict[elem]['column_type'] == "SERIAL":
                assert ('int' in created_table_dict[elem]['column_type'])
                assert created_table_dict[elem]['default_value'] is not None
                assert not created_table_dict[elem]['nullable']
            else:
                assert (created_table_dict[elem]['column_type'] in table_dict[elem]['column_type'] or
                         table_dict[elem]['column_type'] in created_table_dict[elem]['column_type'])

                assert (created_table_dict[elem]['nullable'] == table_dict[elem]['nullable'])
                assert (created_table_dict[elem]['default_value'] is not None and table_dict[elem]['default_value'] is not None) or \
                       (created_table_dict[elem]['default_value'] is None and table_dict[elem]['default_value'] is None)




if __name__ == '__main__':
    unittest.main()