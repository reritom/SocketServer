


server = TestServer(port=12345)

@server.on_startup
def startup(self):
    pass

@server.on_connect
def connect(self, connection_id)
    return self.reply("Hello!")

@server.route('GET:<resource>')
def test_route(resource)
    return server.reply("Getting {}".format(resource))

@server.route('PATCH:<resource>:<data>')
def test_patch(resource, data)
    return server.reply("Getting {}".format(resource))

server.add_route(rule='DEPLOY:ALL', callback=lambda: print("This callback has no parameters"))