from threading import Thread, Event
from queue import Queue
from functools import wraps
import socket, os
from .tools import get_ip
from .route import Route
from .caller import Caller
from .protocols.basic.basic_protocol import BasicProtocol

class SocketServer(Thread):
    protocols = []
    matchers = {}

    def __init__(self, protocol=BasicProtocol):
        super().__init__()
        self.protocol = protocol

        self.stop_flag = Event()
        self.routes = []
        self._connections = []
        self.processed_to_pending = Queue()
        self._incoming_reqeust_queue = Queue()
        self.incoming_request_thread = Thread(target=self.incoming_request_thread_method)

    @staticmethod
    def add_protocol(protocol_class, protocol_matcher):
        SocketServer.protocols.append(protocol_class)
        SocketServer.matchers[protocol_class] = protocol_matcher

    def start(self, port, host=None):
        if host is None:
            host = get_ip()
            print("Host is {}".format(host))

        self.host = host
        self.port = port

        return super().start()

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
                for connection in self._connections:
                    connection.close()
                s.close()
                break

            # Here we process incoming connections
            try:
                conn, addr = s.accept()
                conn.settimeout(0)
                self._connections.append(conn)
                try:
                    caller = Caller(conn)
                    self._on_connect(caller)
                except Exception as e:
                    print("Failed to execute on_connect {}".format(e))
            except:
                pass
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
            processed_connection_indices = []

            for index, connection in enumerate(self._connections):
                try:
                    data = connection.recv(1024).decode('utf-8')

                    # The connection has been closed
                    if not data:
                        closed_connection_indices.append(index)
                        print("Connection closed")
                        continue

                    # Trigger the callback
                    try:
                        protocol = self.protocol.from_buffer(data, connection)
                    except Exception as e:
                        print("Failed to build protocol {}".format(e))

                    dispatch_thread = Thread(target=self.dispatch, args=(protocol,))
                    dispatch_thread.setDaemon(True)
                    dispatch_thread.start()

                    processed_connection_indices.append(index)

                    # Move this connection to the dispatched pool so the protocol handles subseqeunt communications
                    # TODO

                except:
                    # Nothing to read
                    pass

            self._connections = [
                connection
                for index, connection
                in enumerate(self._connections)
                if (index not in closed_connection_indices)
                and (index not in processed_connection_indices)
            ]

            for connection in closed_connection_indices:
                caller = Caller(connection, None)
                self._on_disconnect(caller)

            while not self.processed_to_pending.empty():
                self._connections.append(self.processed_to_pending.get())

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
        """
        Decorator for setting the method to be called on startup (server.start())

        Usage:
        @server.on_startup
        def startup_function():
            # Logic here
        """
        self._on_startup = func

    def _on_startup(self):
        """
        Default startup method, to be overwritten using the decorator
        """
        print("In base _on_startup")

    def route404(self, func):
        self._route404 = func

    def _route404(self, caller):
        print("Running _route404")

    def route(self, pattern, **kwargs):
        """
        Decorator for adding a route to the server

        Usage:
        @server.route('regex_here')
        def function_to_route():
            # Logic here
        """

        def descriptor(func):
            self.add_route(pattern, func, **kwargs)
        return descriptor

    def add_route(self, pattern, func, **kwargs):
        route = Route(pattern, func)
        route.set_kwargs(**kwargs)
        self.routes.append(route)

    def _dispatch_internal(self, route, caller, **kwargs):
        print("In parent dispatch internal")
        try:
            route.callback(caller, **kwargs)
        except Exception as e:
            print("Failed to execute callback {}".format(e))

    def dispatch(self, caller):
        for route in self.routes:
            # The protocol matcher matches the protocol instance against the route
            if self.matchers[self.protocol].match(route, caller):
                # The route parses the request pattern
                match = route.match(caller.pattern)
                print("Route has matched")
                self._dispatch_internal(route, caller, **match.groupdict())
                break
        else:
            try:
                print("No match for {}".format(caller.pattern))
                self._route404(caller)
            except Exception as e:
                print("Failed to execute 404 callback {}".format(e))

        if caller.keep_alive:
            self.processed_to_pending.put(caller._connection)
