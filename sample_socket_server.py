from socket_server import SocketServer
import time

server = SocketServer(port=61000)

"""
@server.on_startup
def startup(self):
    pass

@server.on_connect
def connect(self, connection_id)
    return self.reply("Hello!")
"""

@server.route('GET:<resource>')
def test_route(resource):
    return server.reply("Getting {}".format(resource))

"""
@server.route('PATCH:<resource>:<data>')
def test_patch(resource, data)
    return server.reply("Getting {}".format(resource))

"""
server.add_route(pattern='DEPLOY:ALL', func=lambda: print("This callback has no parameters"))

print("Server routes are {}".format(server.routes))

server.start()
time.sleep(10)
server.stop_flag.set()
server.join()