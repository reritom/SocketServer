from server.http_server import HTTPServer
import time, os

server = HTTPServer(static_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'statics'))

@server.on_startup
def startup(self):
    pass

@server.on_connect
def connect(caller):
    print("In connect")

@server.route('/hi', methods=['GET'])
def test_route(caller):
    print("Executing test_route")
    caller.reply("Getting hi")

@server.route('/example/<resource>', methods=['GET'])
def test_route(caller, resource):
    print("Executing test_route")
    caller.reply({resource: 'Hello'})

@server.route404
def invalid_command(caller):
    print("Not match for request, in custom")
    body = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>400 Bad Request</title></head><body><h1>Bad Request</h1><p>Your browser sent a request that this server could not understand.</p><p>The request line contained invalid characters following the protocol string.</p></body></html>'
    caller.reply(body)

@server.route('/example/<resource>', methods=['PUT'])
def test_patch(caller, resource):
    print(caller.payload)
    print("In test_patch")


print("Server routes are {}".format([route.pattern for route in server.routes]))

server.start(port=60000)
time.sleep(20)
server.stop_flag.set()
server.join()
