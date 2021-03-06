import select
import socket

from server.Client import Client


class Server(object):
    '''
    Threading server
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(('localhost', 50012))

    def run(self):
        self.server.listen(10)
        inputs = [self.server]
        outputs = []
        clients = dict()
        while 1:
            inready, outready, excready = select.select(inputs, outputs, []);

            for s in inready:
                if s == self.server:
                    sock, address = self.server.accept();
                    client = Client()
                    client.setup(sock, address)
                    client.start()
                    clients[client.client] = client
                    outputs.append(client.client)
                else:
                    data = s.recv(1024)
                    for c in outready:
                        if clients[c].isAuthenticated():
                            c.sendall(data)
            for c in outready:
                if clients[c].isAuthenticated():
                    if c not in inputs:
                        print(c, 'authenticated')
                        inputs.append(c)
        self.server.close()


if __name__ == '__main__':
    server = Server()
    server.run()