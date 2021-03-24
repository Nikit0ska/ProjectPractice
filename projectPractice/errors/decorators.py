# from projectPractice.Table import find_type_by_sqltype
# from projectPractice.errors import OdbcError, Error
from projectPractice.sql_types import SQL_CUSTOM_TYPES, find_type_by_sqltype
from projectPractice.errors.errors import *


def err_decor(db_func):
    def wrapper(*args, **kwargs):
        try:
            if len(args) > 0:
                return db_func(*args, **kwargs)
            else:
                return db_func(**kwargs)
        except Error as ex:
            if len(ex.args) > 1:
                raise OdbcError(ex.args[1]) from None
            else:
                raise OdbcError(ex.args[0]) from None
    return wrapper


def decorator_function_with_arguments(sql_type, sql_type_name):
    def wrap(f):
        def wrapped_f(self, name, is_foreign=False):
            sql_name = find_type_by_sqltype(sql_type)
            if sql_name is not None:
                print(is_foreign)
                return f(self, name, is_foreign=is_foreign)
            else:
                raise TypeError(f"ODBC Driver doesn't support '{sql_type_name}' type.")
        return wrapped_f
    return wrap


def decorator_function_with_arguments_with_length(sql_type, sql_type_name):
    def wrap(f):
        def wrapped_f(self, name, length, foreign=False):
            sql_name = find_type_by_sqltype(sql_type)
            if sql_name is not None:
                # print(foreign)
                return f(self, name, length, is_foreign=foreign)
            else:
                raise TypeError(f"ODBC Driver doesn't support '{sql_type_name}' type.")
        return wrapped_f
    return wrap