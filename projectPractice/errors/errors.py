from pyodbc import Error


class OdbcError(Error):
    pass


class OdbcConnectionError(OdbcError):
    pass


class OdbcTypeError(OdbcError):
    pass


class TableError(Error):
    pass
