from threading import Thread, Event
import socket

def get_ip():
    """
    Determine the local IP
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class SocketServerBase(Thread):
    def __init__(self, port, host=None):
        if host is None:
            host = get_ip()

        self.host = host
        self.port = port
        self.stop_flag = Event()
        self._connections = list()

        super().__init__()

        return self.on_init()

    def on_init(self):
        pass

    def on_connect(self, connection):
        pass

    def on_disconnect(self):
        pass

    def on_message(self, connection, message):
        pass

    def run(self):
        """
        Running this thread awaits incoming connections, and also spawns another thread for processing any data coming from the established connections
        """
        print("Serving access point")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            s.settimeout(0)

            dispatch_thread = Thread(target=self.dispatcher)
            dispatch_thread.start()

            while True:
                if self.stop_flag.is_set():
                    print("Killing server")
                    s.close()
                    break

                try:
                    conn, addr = s.accept()
                    conn.settimeout(0)
                    self._connections.append(conn)
                    self.on_connect(connection)
                except Exception as e:
                    continue
                else:
                    print("Connection established")

            dispatch_thread.join()


    def dispatcher(self):
        while True:
            if self.stop_flag.is_set():
                print("Killing dispatcher")
                return

            closed_connection_indices = []

            for index, connection in enumerate(self._connections):
                try:
                    data = connection.recv(1024).decode('utf-8')

                    # The connection has been closed
                    if not data:
                        closed_connection_indices.append(index)
                        print("Connection closed")
                        continue

                    # Trigger the callback
                    self.on_message(connection, data)

                except:
                    # Nothing to read
                    pass

            self._connections = [
                connection
                for index, connection
                in enumerate(self._connections)
                if index not in closed_connection_indices
            ]

            for connection in closed_connection_indices:
                self.on_disconnect(connection)

