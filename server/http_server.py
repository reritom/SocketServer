import os

from .socket_server import SocketServer
from .protocols.http.http_protocol import HTTPProtocol

class HTTPServer(SocketServer):
    static_dir = None

    def __init__(self, static_dir=None):
        super().__init__(HTTPProtocol)

        if static_dir:
            self.add_static_routes(static_dir)
            self.static_dir = static_dir

    def add_static_routes(self, static_dir):
        paths = {}
        for (dirpath, dirnames, filenames) in os.walk(static_dir):
            for filename in filenames:
                paths[os.path.join('statics', os.path.join(dirpath, filename)[len(static_dir):])] = os.path.join(dirpath, filename)

        for path_pattern, resource_path in paths.items():
            self.add_route(path_pattern, self.static_route_callback, methods=['GET'], static=True, resource_location=resource_path)

    def static_route_callback(self, route, caller, **kwargs):
        # Retrieve the route we are in the callback for
        #this_route = reduce(lambda route: route.pattern == caller.pattern, self.routes)
        #print("Returning {}".format(static_path))
        resource_path = route.resource_location

        with open(resource_path, 'rb') as f:
            resource_bytes = f.read()

        caller.reply(resource_bytes)

    def _dispatch_internal(self, route, caller, **kwargs):
        print("In child dispatch internal")
        if hasattr(route, 'static') and route.static:
            print("Performing static retrieval")
            return self.static_route_callback(route, caller, **kwargs)
        else:
            return super()._dispatch_internal(route, caller, **kwargs)
