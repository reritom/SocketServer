from socket_server import SocketServer
import time

server = SocketServer(port=61000)

@server.on_startup
def startup(self):
    pass

@server.on_connect
def connect(caller):
    print("In connect")

@server.route('GET:<resource>')
def test_route(caller,resource):
    print("Executing test_route")
    return


@server.route404
def invalid_command(caller):
    print("Not match for request")

@server.route('PATCH:<resource>:<data>')
def test_patch(caller, resource, data):
    print("In test_patch")

#server.add_route(pattern='DEPLOY:ALL', func=lambda: print("This callback has no parameters"))

print("Server routes are {}".format(server.routes))

server.start()
time.sleep(15)
server.stop_flag.set()
server.join()