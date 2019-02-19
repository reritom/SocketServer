from threading import Thread, Event
from queue import Queue
from functools import wraps
import socket, re, os

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

class Caller:
    def __init__(self, connection):
        self._connection = connection

    def reply(self, message):
        if not isinstance(message, bytes):
            try:
                message = str(message)
                message = bytes(message, 'utf-8')
            except:
                print("Failed to convert reply to sendable format")

        try:
            self._connection.send(message)
        except:
            print("Failed to send reply")

class Route:
    def __init__(self, pattern, callback):
        self.callback = callback
        self.pattern = pattern
        self.regex = self.regex_from_pattern(pattern)
        print("Pattern {} has regex {}".format(pattern, self.regex))

    @staticmethod
    def regex_from_pattern(pattern):
        param_open = False
        index = 0
        re_buffer = ''
        placeholder_buffer = ''
        placeholder_list = []
        re_placeholder = '(?P<{}>.*)'

        while index < len(pattern):
            if param_open:
                if pattern[index] == '>':
                    print("In close in param open")
                    re_buffer +=  re_placeholder.format(placeholder_buffer)
                    placeholder_list.append(placeholder_buffer)
                    print("Placeholder buffer {}".format(placeholder_buffer))
                    placeholder_buffer = ''
                    print("Rebuffer {}".format(re_buffer))
                    param_open = False
                else:
                    placeholder_buffer += pattern[index]

            elif pattern[index] == '<':
                print("Opening param")
                param_open = True

            elif pattern[index] == '>':
                print("Closing param")
                param_open = False

            else:
                re_buffer += pattern[index]
                print("Rebuffer {}".format(re_buffer))

            index += 1

        return re.compile(re_buffer)


    def match(self, value) -> bool:
        """
        Check if the value matches the pattern
        """
        return self.regex.match(value)

class SocketServer(Thread):
    def __init__(self, port, host=None):
        super().__init__()

        if host is None:
            host = get_ip()

        self.port = port
        self.host = host

        self.stop_flag = Event()
        self.routes = []
        self._connections = []
        self._incoming_reqeust_queue = Queue()
        self.incoming_request_thread = Thread(target=self.incoming_request_thread_method)

    def run(self):
        print("Running Server")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen()
        s.settimeout(0)

        self._on_startup(self)
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
                caller = Caller(conn)
                self._on_connect(caller)
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
                    caller = Caller(connection)
                    self.dispatch(caller, data)

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
                caller = Caller(connection)
                self._on_disconnect(caller)

    def on_connect(self, func):
        # Decorator for setting the internal func
        self._on_connect = func

    def on_disconnect(self, func):
        # Decorator for setting the internal func
        self._on_disconnect = func

    def _on_disconnect(self, caller):
        # Function internally called when a connection is terminated
        print("Running _on_disconnect")

    def _on_connect(self, caller):
        # Function internally called when a connection is established
        print("Running _on_connect")

    def on_startup(self, func):
        self._on_startup = func

    def _on_startup(self):
        print("In base _on_startup")

    def route404(self, func):
        self._route404 = func

    def _route404(self, caller):
        print("Running _route404")

    def route(self, pattern):
        def descriptor(func):
            self.add_route(pattern, func)
        return descriptor

    def add_route(self, pattern, func):
        route = Route(pattern, func)
        self.routes.append(route)

    def dispatch(self, caller, message):
        print("Dispatching message")
        for route in self.routes:
            match = route.match(message)
            if match:
                print("Route has matched")
                try:
                    return route.callback(caller, **match.groupdict())
                except Exception as e:
                    print("Failed to execute callback {}".format(e))
        else:
            return self._route404(caller)

