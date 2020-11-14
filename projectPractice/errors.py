from pyodbc import Error


def err_decor(db_func):
    def wrapper(*args):
        try:
            if len(args) > 0:
                db_func(*args)
            else:
                db_func()
        except Error as ex:
            raise OdbcError(ex.args[1]) from None
    return wrapper


class OdbcError(Error):
    pass


class OdbcConnectionError(OdbcError):
    pass



