import threading

import xlrd3

from projectPractice.Connector import Connector
from projectPractice.ConnThread import ConnThread
from projectPractice.Table import *
import projectPractice.errors as errors


# Для MongoDB: https://www.cdata.com/drivers/mongodb/download/odbc/
# Для PosgreSQL: https://ftp.postgresql.org/pub/odbc/versions/msi/psqlodbc_12_02_0000.zip
# Посмотреть установленные драйвера: pyodbc.drivers()


def db_connect(driver, server, port, db, user='', password='', autocomm=True):
    conn = Connector(driver, server, port, db, uid=user, pwd=password, autocommit=autocomm)
    thread = ConnThread(conn)
    thread.start()


def __get_conn_thread():
    con_thread = None
    for thread in threading.enumerate():
        if type(thread) == ConnThread:
            con_thread = thread
            return con_thread
    if con_thread is None:
        raise errors.OdbcConnectionError('No connection')


@errors.err_decor
def db_disconnect():
    conn_thread = __get_conn_thread()
    conn_thread.stop_thread()
    return None


@errors.err_decor
def db_read_table(table, limit=0, sql_condition='', order_by=('', '')):
    conn = __get_conn_thread().connector
    if type(table) == CreatedTable:
        return table.get_data()
    query = f'SELECT * FROM {table}'
    if sql_condition != '':
        query += f" where {sql_condition}"
    if order_by != ('', ''):
        query += f" order by {order_by[0]} {order_by[1]}"
    if limit != 0:
        query += f" limit {limit}"
    query += ';'
    conn.execute(query)
    return conn.cursor.fetchall()


@errors.err_decor
def db_execute_query(query):
    conn = __get_conn_thread().connector
    if 'select' in query.lower():
        content = conn.execute(query)
        return content.fetchall()
    else:
        conn.execute(query)
        return 1


@errors.err_decor
def db_create(db_name):
    conn = __get_conn_thread().connector
    conn.execute(f"CREATE DATABASE {db_name};")
    return True


@errors.err_decor
def db_drop(db_name):
    conn = __get_conn_thread().connector
    conn.execute(f"DROP DATABASE {db_name};")
    return True


@errors.err_decor
def db_change(db_name):
    conn = __get_conn_thread().connector
    params = conn.con_params
    db_disconnect()
    db_connect(params['driver'], params['server'], params['port'], db_name, params['user'], params['password'],
               params['autocommit'])


def __get_dict_csv(path, delimiter, quotechar):
    import csv
    fields = []
    return_data = []
    counter = 0
    with open(path) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
        for row in spamreader:
            temp = {}
            if counter == 0:
                for field in row:
                    fields.append([field.replace(' ', ''), 'real'])
                    counter += 1
                    continue
            else:
                for i in range(len(row)):
                    if row[i].replace(" ", "") != '' and fields[i][1] == 'real' and not (
                    row[i].replace(" ", "").isdigit()):
                        fields[i][1] = 'varchar(255)'
                    temp[fields[i][0]] = row[i].replace(" ", "")
            return_data.append(temp)
            counter += 1
    return_data[0] = fields
    print(return_data)
    return return_data


def __get_field_type(d, field_name):
    for f, t in d:
        if f == field_name:
            return t


def import_csv_db(table_name, path, delimiter=',', quotechar=';'):
    data = __get_dict_csv(path, delimiter, quotechar)
    sql_ct = f"CREATE TABLE {table_name}("
    for field in data[0]:
        sql_ct += f"{field[0]} {field[1]} NULL, "
    sql_ct = sql_ct.rstrip(', ')
    sql_ct += ");"
    db_execute_query(sql_ct)
    for row in data[1:]:
        if row != {}:
            sql_insert = f"INSERT INTO {table_name} VALUES ("
            for elem in row:
                if __get_field_type(data[0], elem) == 'real':
                    if row[elem] == '':
                        sql_insert += f"NULL, "
                    else:
                        sql_insert += f"{int(row[elem])}, "
                else:
                    sql_insert += f"'{(row[elem])}', "
            sql_insert = sql_insert.rstrip(', ')
            sql_insert += ");"
            # print(sql_insert)

            db_execute_query(sql_insert)


def import_xl_db(table_name, path):
    book = xlrd3.open_workbook(path)
    sh = book.sheet_by_index(0)
    fields = [[i.value, set()] for i in sh.row(0)]
    data = []

    for row in range(1, sh.nrows):
        temp_arr = []
        for col in range(sh.ncols):
            cell = sh[row][col]
            temp_arr.append(cell.value)
            fields[col][1].add(cell.ctype)
        data.append(temp_arr)

    for elem in fields:
        if len(elem[1]) > 1:
            elem[1] = {xlrd3.XL_CELL_TEXT}
        cell_type = elem[1].pop()
        if cell_type == xlrd3.XL_CELL_DATE:
            elem[1] = 'date'
        elif cell_type == xlrd3.XL_CELL_TEXT:
            elem[1] = 'varchar(255)'
        elif cell_type == xlrd3.XL_CELL_BOOLEAN:
            elem[1] = 'boolean'
        elif cell_type == xlrd3.XL_CELL_NUMBER:
            elem[1] = 'real'

    sql = f"CREATE TABLE {table_name}("
    for elem in fields:
        sql += f"{elem[0].replace(' ', '')} {elem[1]} NULL, "
    sql = sql.rstrip(", ")
    sql += ");"
    db_execute_query(sql)
    for row in data:
        sql = f"INSERT INTO {table_name} VALUES("
        for col in range(len(row)):
            if fields[col][1] == 'varchar(255)':
                sql += f"'{row[col]}', "
            elif fields[col][1] == 'date':
                date = xlrd3.xldate_as_datetime(row[col], book.datemode)
                sql += f"'{str(date.date())}', "
            else:
                sql += f"{row[col]}, "
        sql = sql.rstrip(", ")
        sql += ");"
        db_execute_query(sql)
    return True

