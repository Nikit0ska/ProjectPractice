import threading
from projectPractice.errors import OdbcConnectionError


class ConnThread(threading.Thread):
    def __init__(self, connector):
        for thread in threading.enumerate():
            if type(thread) == ConnThread:
                raise OdbcConnectionError('Connection already exist')
        super().__init__(target=self.__inf, daemon=True)
        self.connector = connector

    def __inf(self):
        while True:
            if not self.connector.is_connected:
                break

    def stop_thread(self):
        self.connector.close_connection()
        self.join()


def __get_conn_thread():
    con_thread = None
    for thread in threading.enumerate():
        if type(thread) == ConnThread:
            con_thread = thread
            return con_thread
    if con_thread is None:
        raise OdbcConnectionError('No connection')


def get_cursor():
    return __get_conn_thread().connector.cursor