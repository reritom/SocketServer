from server.socket_server import SocketServer
from server.protocols.http import HTTPProtocol
from server.protocols.basic import BasicProtocol
import time

server = SocketServer(protocol=HTTPProtocol)

@server.on_startup
def startup(self):
    pass

@server.on_connect
def connect(caller):
    print("In connect")

@server.route('/example/<resource>', methods=['GET'])
def test_route(caller, resource):
    print("Executing test_route")
    time.sleep(5)
    caller.reply("Getting {}".format(resource))

@server.route404
def invalid_command(caller):
    print("Not match for request, in custom")
    body = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>400 Bad Request</title></head><body><h1>Bad Request</h1><p>Your browser sent a request that this server could not understand.</p><p>The request line contained invalid characters following the protocol string.</p></body></html>'
    caller.reply('HTTP/1.1 200 OK\r\nCache-Control: no-cache, private\r\nContent-Length: {}\r\nDate: Mon, 24 Nov 2014 10:21:21 GMT\r\n\r\n'.format(len(bytes(body, 'utf-8'))))
    caller.reply(body)

@server.route('/example/<resource>', methods=['PUT'])
def test_patch(caller, resource, data):
    print(caller.payload)
    print("In test_patch")


print("Server routes are {}".format(server.routes))

server.start(port=61000)
time.sleep(20)
server.stop_flag.set()
server.join()
