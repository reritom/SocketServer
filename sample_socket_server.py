from server.socket_server import SocketServer
import time

server = SocketServer(port=61000)

@server.on_startup
def startup(self):
    pass

@server.on_connect
def connect(caller):
    print("In connect")

@server.route('GET:<resource>')
def test_route(caller, resource):
    print("Executing test_route")
    time.sleep(5)
    caller.reply("Getting {}".format(resource))

@server.route404
def invalid_command(caller):
    print("Not match for request")

@server.route('PATCH:<resource>:<data>')
def test_patch(caller, resource, data):
    print("In test_patch")

server.add_route(pattern='DEPLOY:ALL', func=lambda caller: caller.reply("Deploying all"))

print("Server routes are {}".format(server.routes))

server.start()
time.sleep(20)
server.stop_flag.set()
server.join()