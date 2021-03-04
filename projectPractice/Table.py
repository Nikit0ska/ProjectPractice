from pyodbc import *

from projectPractice.sql_types import *
from projectPractice.db_funcs import *
from projectPractice.errors import *
# from projectPractice.errors.decorators import decorator_function_with_arguments


class Field:
    def __init__(self, name, type):
        self._field_name = name
        self._field_type = type
        self._params = []

    def default(self, default_value):
        self._params.append(f"DEFAULT '{default_value}'")
        return self

    def nullable(self, flag):
        if flag:
            self._params.append(f"NULL")
        else:
            self._params.append("NOT NULL")
        return self

    def autoincrement(self):
        db = get_db_name()
        print(db)
        if db.lower() == "postgresql":
            self._field_type = "SERIAL"
        else:
            self._params.append('autoincrement')
        return self

    def primary_key(self):
        self._params.append('primary key')
        return self

    def unique(self):
        self._params.append('unique')
        return self


class ForeignField:
    def __init__(self, name, type):
        self._field_name = name
        self._field_type = type
        self._params = {"constraint": '', "foreign_key": f"FOREIGN KEY({self._field_name})",
                        "references": '', 'on_delete': ''}

    def constraint(self, constraint):
        self._params["constraint"] = f"CONSTRAINT {constraint}"
        return self

    def references(self, table, field):
        self._params["references"] = f"REFERENCES {table}({field})"
        return self

    def on_delete(self, set_null=False, set_default=False, restrict=False, cascade=False):
        if set_null:
            self._params["on_delete"] = f"ON DELETE SET NULL"
            return self
        elif set_default:
            self._params["on_delete"] = f"ON DELETE SET DEFAULT"
            return self
        elif restrict:
            self._params["on_delete"] = f"ON DELETE RESTRICT"
            return self
        elif cascade:
            self._params["on_delete"] = f"ON DELETE CASCADE"
            return self


class CreatedTable:
    def __init__(self, table_name):
        self.table = table_name
        self.columns = {}
        db_execute_query(f"select * from {self.table} LIMIT 1")
        cursor = get_cursor()
        columns = [column[0] for column in cursor.description]
        columns_type = [column[1] for column in cursor.description]

        for i in range(len(cursor.description)):
            self.columns[columns[i]] = columns_type[i]

        self.selected_data = []

    def get_data(self):
        return db_read_table(self.table)

    def find(self, id, name_id_field='id'):
        self.selected_data.extend(db_execute_query(f"select {', '.join(self.columns)} from {self.table} where {name_id_field}={id}"))
        return self

    def where(self, column, sql_operator, value):
        if type(value) == str:
            self.selected_data.extend(db_execute_query(f"select {', '.join(self.columns)} from {self.table} where {column} {sql_operator} '{value}'"))
        else:
            self.selected_data.extend(db_execute_query(
                f"select {', '.join(self.columns)} from {self.table} where {column} {sql_operator} {value}"))
        return self

    def get_selected_data(self):
        return self.__make_dict_data(self.selected_data)

    def clear_selected_data(self):
        self.selected_data = []
        return self

    def delete(self):
        data = self.get_selected_data()
        for elem in data:
            sql = f"DELETE FROM {self.table} WHERE "
            for key in elem:
                if type(elem[key]) == str:
                    sql += f"{key} = '{elem[key]}' and "
                else:
                    sql += f"{key} = {elem[key]} and "
            sql = sql.rstrip("and ")
            sql += ";"
            db_execute_query(sql)
        return True

    def update(self, **kwargs):
        data = self.get_selected_data()
        for elem in data:
            sql = f"UPDATE {self.table} SET "
            for value in kwargs:
                if type(kwargs[value]) == str:
                    sql += f"{value} = '{kwargs[value]}'"
                else:
                    sql += f"{value} = {kwargs[value]}"
                sql += ', '
            sql = sql.rstrip(', ')
            sql += " WHERE "
            for key in elem:
                if type(elem[key]) == str:
                    sql += f"{key} = '{elem[key]}' and "
                elif elem[key] is None:
                    sql += f"{key} is NULL and "
                else:
                    sql += f"{key} = {elem[key]} and "
            sql = sql.rstrip("and ")
            sql += ";"
            db_execute_query(sql)
        return True

    def get_form_data(self):
        data = db_execute_query(f"SELECT {', '.join(self.columns)} FROM {self.table}")
        return self.__make_dict_data(data)

    def __make_dict_data(self, data):
        new_data = []
        for elem in data:
            tmp = {}
            keys = list(self.columns.keys())
            for i in range(len(elem)):
                tmp[keys[i]] = elem[i]
            new_data.append(tmp)
        return new_data

    def insert(self, collection=list() or dict() or tuple(), **kwargs):
        if len(collection) > 0:
            if type(collection) == dict:
                db_execute_query(self._query_dict_insert(collection))
                # db_execute_query(self._query_dict_insert(collection))
                return True
            else:
                db_execute_query(self._query_list_insert(collection))
                return True
        elif len(kwargs) > 0:
            db_execute_query(self._query_dict_insert(kwargs))
            return True
        else:
            db_execute_query(f'INSERT INTO {self.table} VALUES ()')
            return True

    def __sql_tuple(self, values):
        query = "("
        for elem in values:
            if type(elem) != str or elem.upper() == 'DEFAULT':
                query += str(elem)
                query += ", "
            else:
                query += f"'{elem}'"
                query += ", "
        query = query.rstrip(" ,")
        query += ");"
        return query

    def _query_list_insert(self, collection):
        query = f"INSERT INTO {self.table} VALUES "
        query += self.__sql_tuple(collection)
        return query

    def _query_dict_insert(self, dict):
        keys = tuple(dict)
        values = tuple(dict.values())
        query = f"INSERT INTO {self.table}("
        for elem in keys:
            query += f"{elem}"
            query += ", "
        query = query.rstrip(" ,")
        query += ") VALUES "
        query += self.__sql_tuple(values)

        return query

    def drop(self):
        db_execute_query(f"DROP TABLE {self.table}")
        return True

    def __getattr__(self, item):
        if item in dir(NewTable):
            raise TableError(f"Method '{item}' is for only creating tables. Table {self.table} already created.")


class NewTable:

    def __init__(self, table_name):
        self.table = table_name
        self.fields = []

    def id(self):
        # db = get_db_name()
        # print(db)

        # field = self.integer('id').autoincrement()

        field = self.integer("id").autoincrement()
        field.unique()
        field.primary_key()

    def integer(self, name, is_foreign=False):
        field_type = find_type_by_sqltype(SQL_INTEGER)

        if is_foreign:
            field = ForeignField(name, field_type)
            self.fields.append(field)
            return field
        field = Field(name, field_type)
        self.fields.append(field)
        return field


    @decorator_function_with_arguments(SQL_TEXT, "Text")
    def text(self, name, is_foreign=False):
        field_type = find_type_by_sqltype(SQL_TEXT)

        if is_foreign:
            field = ForeignField(name, field_type)
            self.fields.append(field)
            return field
        field = Field(name, field_type)
        self.fields.append(field)
        return field

    # @decorator_function_with_arguments(SQL_VARCHAR, "String")
    def string(self, name, length, is_foreign=False):
        field_type = find_type_by_sqltype(SQL_VARCHAR)
        if is_foreign:
            field = ForeignField(name, f'{field_type}({length})')
            self.fields.append(field)
            return field
        field = Field(name, f'{field_type}({length})')
        self.fields.append(field)
        return field

    @decorator_function_with_arguments(SQL_BIT, "Boolean")
    def bool(self, name, is_foreign=False):
        field_type = find_type_by_sqltype(SQL_BIT)

        if is_foreign:
            field = ForeignField(name, field_type)
            self.fields.append(field)
            return field
        field = Field(name, field_type)
        self.fields.append(field)
        return field


    def binary(self, name, is_foreign=False):
        field_type = find_type_by_sqltype(SQL_BINARY)

        if is_foreign:
            field = ForeignField(name, field_type)
            self.fields.append(field)
            return field
        field = Field(name, field_type)
        self.fields.append(field)
        return field

    def char(self, name, is_foreign=False):
        field_type = find_type_by_sqltype(SQL_CHAR)

        if is_foreign:
            field = ForeignField(name, field_type)
            self.fields.append(field)
            return field
        field = Field(name, field_type)
        self.fields.append(field)
        return field


    def real(self, name, is_foreign=False):
        field_type = find_type_by_sqltype(SQL_REAL)

        if is_foreign:
            field = ForeignField(name, field_type)
            self.fields.append(field)
            return field
        field = Field(name, field_type)
        self.fields.append(field)
        return field

    def float(self, name, is_foreign=False):
        field_type = find_type_by_sqltype(SQL_FLOAT)

        if is_foreign:
            field = ForeignField(name, field_type)
            self.fields.append(field)
            return field
        field = Field(name, field_type)
        self.fields.append(field)
        return field


    def create_table(self):
        sql = f"CREATE TABLE {self.table}("
        for elem in self.fields:
            tmp = f"{elem._field_name} {elem._field_type}"
            if type(elem) != ForeignField:
                for param in elem._params:
                    tmp += f" {param}"
            tmp += ", "
            sql += tmp
            tmp = ''
        for elem in self.fields:
            if type(elem) == ForeignField:
                for param in elem._params:
                    tmp += f" {elem._params[param]}"
                tmp += ", "
                sql += tmp
        sql = sql.rstrip(', ')
        sql += ");"
        print(sql)
        db_execute_query(sql)
        return True


class Table:
    def __new__(cls, table_name):
        try:
            db_execute_query(f"select * from {table_name}")
        except OdbcError:
            return NewTable(table_name)

        return CreatedTable(table_name)
