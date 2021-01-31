from pyodbc import Error


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


class OdbcError(Error):
    pass


class OdbcConnectionError(OdbcError):
    pass


class OdbcTypeError(OdbcError):
    pass


class TableError(Error):
    pass
