from socket_server import SocketServer

server = SocketServer(port=12345)
server.start()
server.stop_flag.set()
server.join()