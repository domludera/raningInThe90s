import socket

class SocketClient:

    def __init__(self, port):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect(('localhost', port))

    def run(self):
        self._s.sendall(b'Hello\n')
        return self._s.recv(1024)

