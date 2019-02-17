from threading import Thread, Event
from queue import Queue
from functools import wraps
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

class SocketServer(Thread):
    def __init__(self, port, host=None):
        super().__init__()

        if host is None:
            host = get_ip()

        self.port = port
        self.host = host

        self.stop_flag = Event()
        self.routes = {}
        self._connections = []
        self._incoming_reqeust_queue = Queue()
        self.incoming_request_thread = Thread(target=self.incoming_request_thread_method)

    def run(self):
        """
        Running this thread awaits incoming connections, and also spawns another thread for processing any data coming from the established connections
        """
        print("Serving access point")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen()
        s.settimeout(0)

        self.incoming_request_thread.start()

        while True:
            if self.stop_flag.is_set():
                print("Main stop flag is set")
                break

            # Here we process incoming connections
            try:
                conn, addr = s.accept()
                conn.settimeout(0)
                self._connections.append(conn)
                self._on_connect(conn)
            except Exception as e:
                continue
            else:
                print("Connection established")

        self.incoming_request_thread.join()
        s.close()

    def incoming_request_thread_method(self):
        print("Running incoming request thread")
        while True:
            if self.stop_flag.is_set():
                print("Killing incoming_request_thread_method")
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
                    self.dispatch(connection, data)

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
                self._on_disconnect(connection)

    def on_connect(self, func):
        # Decorator for setting the internal func
        self._on_connect = func

    def on_disconnect(self, func):
        # Decorator for setting the internal func
        self._on_disconnect = func

    def _on_disconnect(self, connection):
        # Function internally called when a connection is terminated
        print("Running _on_disconnect")
        pass

    def _on_connect(self, connection):
        # Function internally called when a connection is established
        print("Running _on_connect")
        pass

    def route(self, pattern):
        def descriptor(func):
            """
            @wraps(func)
            class FuncWrapper:
                def __init__(self):
                    self.context = {}
                    self.func = func

                def __call__(self, *args, **kwargs):
                    return self.func(*args, **kwargs)

            self.add_route(pattern, FuncWrapper())
            """
            self.add_route(pattern, func)

        return descriptor

    def add_route(self, pattern, func):
        self.routes[pattern] = func

    def dispatch(self, connection, message):
        print("Dispatching message")