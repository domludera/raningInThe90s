import socket

class SocketClient:

    def __init__(self, port):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect(('localhost', port))

    def run(self):
        msg = "hello world!"
        self._s.sendall(bytes(msg, 'utf-8'))
