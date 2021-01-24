from projectPractice import db_funcs
from projectPractice.errors import OdbcError


def get_sup_type(some_type):
    for elem in db_funcs.DATA_TYPES:
        if elem in some_type or some_type in elem:
            return elem


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
        db_funcs.db_execute_query(f"select * from {self.table} LIMIT 1")
        cursor = db_funcs.get_cursor()
        columns = [column[0] for column in cursor.description]
        columns_type = [column[1] for column in cursor.description]

        for i in range(len(cursor.description)):
            self.columns[columns[i]] = columns_type[i]

        self.selected_data = []

    def get_data(self):
        return db_funcs.db_read_table(self.table)

    def find(self, id, name_id_field='id'):
        self.selected_data.extend(db_funcs.db_execute_query(f"select {', '.join(self.columns)} from {self.table} where {name_id_field}={id}"))
        return self

    def where(self, column, sql_operator, value):
        if type(value) == str:
            self.selected_data.extend(db_funcs.db_execute_query(f"select {', '.join(self.columns)} from {self.table} where {column} {sql_operator} '{value}'"))
        else:
            self.selected_data.extend(db_funcs.db_execute_query(
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
            db_funcs.db_execute_query(sql)
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
            db_funcs.db_execute_query(sql)
        return True

    def get_form_data(self):
        data = db_funcs.db_execute_query(f"SELECT {', '.join(self.columns)} FROM {self.table}")
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
                db_funcs.db_execute_query(self._query_dict_insert(collection))
                # db_execute_query(self._query_dict_insert(collection))
                return True
            else:
                db_funcs.db_execute_query(self._query_list_insert(collection))
                return True
        elif len(kwargs) > 0:
            db_funcs.db_execute_query(self._query_dict_insert(kwargs))
            return True
        else:
            db_funcs.db_execute_query(f'INSERT INTO {self.table} VALUES ()')
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
        db_funcs.db_execute_query(f"DROP TABLE {self.table}")
        return True


class NewTable:

    def __init__(self, table_name):
        self.table = table_name
        self.fields = []

    def id(self):
        field = Field('id', 'serial')
        field._params.append('UNIQUE')
        field._params.append('PRIMARY KEY')
        self.fields.append(field)

    def autoincrement(self, name):
        field = Field(name, 'serial')
        self.fields.append(field)
        return field

    def integer(self, name, is_foreign=False):
        field_type = get_sup_type('int')
        if field_type is not None:
            if is_foreign:
                field = ForeignField(name, field_type)
                self.fields.append(field)
                return field
            field = Field(name, field_type)
            self.fields.append(field)
            return field
        else:
            raise TypeError("ODBC Driver doesn't support 'integer' type")

    def text(self, name, is_foreign=False):
        field_type = get_sup_type('text')
        if field_type is not None:
            if is_foreign:
                field = ForeignField(name, 'text')
                self.fields.append(field)
                return field
            field = Field(name, 'text')
            self.fields.append(field)
            return field
        else:
            raise TypeError("ODBC Driver doesn't support 'text' type")

    def string(self, name, length, is_foreign=False):
        field_type = get_sup_type('varchar')
        if field_type is None:
            field_type = get_sup_type('string')
        if field_type is not None:
            if is_foreign:
                field = ForeignField(name, f'{field_type}({length})')
                self.fields.append(field)
                return field
            field = Field(name, f'{field_type}({length})')
            self.fields.append(field)
            return field
        else:
            raise TypeError("ODBC Driver doesn't support 'string' type")

    def bool(self, name, is_foreign=False):
        field_type = get_sup_type('bool')
        if field_type is not None:
            if is_foreign:
                field = ForeignField(name, field_type)
                self.fields.append(field)
                return field
            field = Field(name, field_type)
            self.fields.append(field)
            return field
        else:
            raise TypeError("ODBC Driver doesn't support 'bool' type")

    def binary(self, name, is_foreign=False):
        field_type = get_sup_type('binar')
        if field_type is not None:
            if is_foreign:
                field = ForeignField(name, field_type)
                self.fields.append(field)
                return field
            field = Field(name, field_type)
            self.fields.append(field)
            return field
        else:
            raise TypeError("ODBC Driver doesn't support 'binary' type")

    def char(self, name, is_foreign=False):
        field_type = get_sup_type('char')
        if field_type is not None:
            if is_foreign:
                field = ForeignField(name, field_type)
                self.fields.append(field)
                return field
            field = Field(name, field_type)
            self.fields.append(field)
            return field
        else:
            raise TypeError("ODBC Driver doesn't support 'char' type")

    def real(self, name, is_foreign=False):
        field_type = get_sup_type('real')
        if field_type is not None:
            if is_foreign:
                field = ForeignField(name, field_type)
                self.fields.append(field)
                return field
            field = Field(name, field_type)
            self.fields.append(field)
            return field
        else:
            raise TypeError("ODBC Driver doesn't support 'real' type")

    def float(self, name, is_foreign=False):
        field_type = get_sup_type('float')
        if field_type is None:
            field_type = get_sup_type('double')
        if field_type is not None:
            if is_foreign:
                field = ForeignField(name, field_type)
                self.fields.append(field)
                return field
            field = Field(name, field_type)
            self.fields.append(field)
            return field
        else:
            raise TypeError("ODBC Driver doesn't support 'float' type")

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

        db_funcs.db_execute_query(sql)
        return True


class Table:
    def __new__(cls, table_name):
        try:
            db_funcs.db_execute_query(f"select * from {table_name}")
        except OdbcError:
            return NewTable(table_name)

        return CreatedTable(table_name)
