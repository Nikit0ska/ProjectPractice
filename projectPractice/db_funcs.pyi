from projectPractice.ConnThread import ConnThread

def __get_conn_thread() -> ConnThread:...
def db_connect(driver: str, server: str, port: str or int, db: str, user='', password='') -> None:...
def db_disconnect() -> None:...
def db_read_table(table_name: str) -> list:...
def db_execute_query(query: str) -> None:...