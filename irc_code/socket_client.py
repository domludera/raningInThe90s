import socket

class SocketClient:

    def __init__(self, port):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect(('localhost', port))

    def run(self):
        self._s.sendall(bytes(input(), 'utf-8'))
        data = self._s.recv(1024)
        return data

