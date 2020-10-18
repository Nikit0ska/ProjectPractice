import mysql.connector
from mysql.connector import Error


def create_connection(host_name, user_name, user_password, db_name=''):
    connection = None
    try:
        if db_name != '':
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name
            )
            print("Connection to MySQL DB successful")
        else:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
            )
            print("Connection to MySQL successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def create_db(connection, db_name):
    cursor = connection.cursor()
    try:
        cursor.execute(f"CREATE DATABASE {db_name}")
        connection.commit()
        print("Database created successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


connection = create_connection('localhost', 'root', '',)

