from .socket_server import SocketServer

from .protocols.http.http_matcher import HTTPMatcher
from .protocols.http.http_protocol import HTTPProtocol

SocketServer.add_protocol(HTTPProtocol, HTTPMatcher)


from .protocols.basic.basic_matcher import BasicMatcher
from .protocols.basic.basic_protocol import BasicProtocol

SocketServer.add_protocol(BasicProtocol, BasicMatcher)
