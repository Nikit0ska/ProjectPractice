from projectPractice import db_funcs


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
        data = db_funcs.db_execute_query(f"select column_name,data_type from information_schema.columns "
                                f"where table_name = '{table_name}';")

        for elem in data:
            self.columns[elem[0]] = elem[1]

    def get_data(self):
        return db_funcs.db_read_table(self.table)

    def get_form_data(self):
        data = db_funcs.db_read_table(self.table)
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
        self.fields.append(field)

    def integer(self, name, is_foreign=False):
        if is_foreign:
            field = ForeignField(name, 'integer')
            self.fields.append(field)
            return field
        field = Field(name, 'integer')
        self.fields.append(field)
        return field

    def text(self, name, is_foreign=False):
        field = Field(name, 'text')
        self.fields.append(field)
        return field

    def string(self, name, length, is_foreign=False):
        field = Field(name, f'varchar({length})')
        self.fields.append(field)
        return field

    def bool(self, name, is_foreign=False):
        field = Field(name, 'boolean')
        self.fields.append(field)
        return field

    def binary(self, name, is_foreign=False):
        field = Field(name, 'bytea')
        self.fields.append(field)
        return field

    def char(self, name, is_foreign=False):
        field = Field(name, 'char')
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
        # db_funcs.db_execute_query(sql)
        # return Table(self.table)


class Table:
    def __new__(cls, table_name):
        a = db_funcs.db_execute_query(f"select * from pg_tables where tablename='{table_name}'")
        if len(a) == 0:
            return NewTable(table_name)
        else:
            return CreatedTable(table_name)
