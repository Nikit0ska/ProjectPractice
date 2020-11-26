from projectPractice.db_funcs import *


class Field:
    def __init__(self, name, type):
        self._field_name = name
        self._field_type = type
        self._params = []

    def autoincrement(self):
        self._params.append('SERIAL')
        return self

    def default(self, default_value):
        self._params.append(f"DEFAULT '{default_value}'")
        return self

    def nullable(self, flag):
        if flag:
            self._params.append(f"NULL")
        else:
            self._params.append("NOT NULL")
        return self


class CreatedTable:
    def __init__(self, table_name):
        self.table = table_name
        self.columns = {}
        data = db_execute_query(f"select column_name,data_type from information_schema.columns "
                                f"where table_name = '{table_name}';")

        for elem in data:
            self.columns[elem[0]] = elem[1]

    def get_data(self):
        return db_read_table(self.table)

    def get_form_data(self):
        data = db_read_table(self.table)
        new_data = []
        for elem in data:
            tmp = {}
            keys = list(self.columns.keys())
            for i in range(len(elem)):
                tmp[keys[i]] = elem[i]
            new_data.append(tmp)
        return new_data

    def insert(self, *args):
        if len(args) == 1:
            query = f"INSERT INTO {self.table} VALUES ({args[0]})"
        else:
            query = f"INSERT INTO {self.table} VALUES {args}"
        db_execute_query(query)
        return True

    def drop(self):
        db_execute_query(f"DROP TABLE {self.table}")
        return True


class NewTable:
    def __init__(self, table_name):
        self.table = table_name
        self.fields = []

    def id(self):
        field = Field('id', 'serial')
        field._params.append('UNIQUE')
        self.fields.append(field)

    def integer(self, name):
        field = Field(name, 'integer')
        self.fields.append(field)
        return field

    def text(self, name):
        field = Field(name, 'text')
        self.fields.append(field)
        return field

    def string(self, name, length):
        field = Field(name, f'varchar({length})')
        self.fields.append(field)
        return field

    def create_table(self):
        sql = f"CREATE TABLE {self.table}("
        for elem in self.fields:
            tmp = f"{elem._field_name} {elem._field_type}"
            for param in elem._params:
                tmp += f" {param}"
            tmp += ", "
            sql += tmp
        sql = sql.rstrip(', ')
        sql += ");"
        return sql


class Table:
    def __new__(cls, table_name):
        a = db_execute_query(f"select * from pg_tables where tablename='{table_name}'")
        if len(a) == 0:
            return NewTable(table_name)
        else:
            return CreatedTable(table_name)

# class NewTable:
#     def __init__(self, table_name):
#         self.table = table_name
#         self.columns = []
#         self.query = "CREATE TABLE("
#
#     def id(self):
#         self.columns.append({'id' : []})
#
#     def create_table(self):
#         pass