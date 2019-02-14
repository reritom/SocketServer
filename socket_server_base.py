from threading import Thread
import socket

def get_ip():
    """
    Determine the local IP
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class SocketServerBase(Thread):
    def __init__(self, port, host=None):
        if host is None:
            host = get_ip()

        self.host = host
        self.port = port

        super().__init__()

    def run(self):
        pass