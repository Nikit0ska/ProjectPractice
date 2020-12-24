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
                    if row[i].replace(" ", "") != '' and fields[i][1] == 'real' and not(row[i].replace(" ", "").isdigit()):
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


def __get_fields_dict(path):
    book = xlrd3.open_workbook(path)
    sh = book.sheet_by_index(0)
    fields = []

    for elem in sh.row(0):
        field_name = (str(elem).split(":")[1].replace("'", ""))
        fields.append([field_name, set()])

    for i in range(1, sh.nrows):
        for j in range(sh.ncols):
            if sh.cell_type(i, j) is xlrd3.XL_CELL_TEXT:
                fields[j][1].add("varchar(255)")

            elif sh.cell_type(i, j) is xlrd3.XL_CELL_NUMBER:
                fields[j][1].add("real")

            elif sh.cell_type(i, j) is xlrd3.XL_CELL_BOOLEAN:
                fields[j][1].add("bool")

            elif sh.cell_type(i, j) is xlrd3.XL_CELL_DATE:
                fields[j][1].add("date")

    for i in range(len(fields)):
        if len(fields[i][1]) != 1:
            fields[i][1] = {'text'}
        fields[i][1] = str(fields[i][1])[2:-2]
    return fields



def __get_data_arr(path, fields):
    book = xlrd3.open_workbook(path)
    sh = book.sheet_by_index(0)
    data = []
    for i in range(1, sh.nrows):
        temp_data = []
        for j in range(sh.ncols):
            if (fields[j][1] == 'date'):
                date = xlrd3.xldate_as_datetime(sh[i][j].value, book.datemode)
                temp_data.append(f"'{str(date.date())}'")
            elif (fields[j][1] == 'varchar(255)'):
                temp_data.append(f"'{sh[i][j].value}'")
            else:
                temp_data.append(sh[i][j].value)
        data.append(temp_data)
    return data


def import_xl_db(table_name, path):
    fields = __get_fields_dict(path)
    sql = f"CREATE TABLE {table_name}("
    for field in fields:
        sql += f"{field[0].replace(' ', '_')} {field[1]} NULL, "
    sql = sql.rstrip(", ")
    sql += ");"
    db_funcs.db_execute_query(sql)
    data = __get_data_arr(path, fields)
    for elem in data:
        sql = f"INSERT INTO {table_name} VALUES("
        for value in elem:
            sql += f"{value}, "
        sql = sql.rstrip(", ")
        sql += ");"
        db_funcs.db_execute_query(sql)
    return True
