import threading


class ConnThread(threading.Thread):
    def __init__(self, connector):
        for thread in threading.enumerate():
            if type(thread) == ConnThread:
                raise ConnectionError
        super().__init__(target=self.__inf, daemon=True)
        self.connector = connector

    def __inf(self):
        while True:
            if not self.connector.is_connected:
                break

    def stop_thread(self):
        self.connector.close_connection()
        self.join()
