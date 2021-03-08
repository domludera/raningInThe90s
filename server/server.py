import errno
import select
import socket

from server_thread import ServerThread


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
        self.server.listen()
        inputs = [self.server]
        outputs = []
        clients = dict()
        while 1:

                inready, outready, excready = select.select(inputs, outputs, inputs)

                for s in inready:
                    if s == self.server:
                        sock, address = self.server.accept();
                        serverThread = ServerThread()
                        serverThread.setup(sock, address, self)
                        serverThread.start()
                        clients[serverThread.client] = serverThread
                        outputs.append(serverThread.client)
                    else:
                        try:
                            data = s.recv(1024)
                            print(data)
                        except socket.error as e:
                            if e.errno == errno.ECONNRESET:
                                data = None
                            else:
                                raise e
                        if data:
                            for c in outready:
                                if clients[c].joinedChannel:
                                    c.sendall(data)
                        else:
                            print(s, 'has disconnected')
                            # inputs.remove(s)
                            outputs.remove(s)
                            del clients[s]
                            s.close()
                for c in outready:
                    try:
                        if int(c.fileno()) > 0:
                            if clients[c].joinedChannel:
                                if c not in inputs:
                                    inputs.append(c)
                        else:
                            inputs.remove(s)
                    except socket.error as e:
                            if e.errno == errno.ECONNRESET:
                                data = None
                            else:
                                raise e

                for err in excready:
                    inputs.remove(err)
                    outputs.remove(err)
                    del clients[err]
                    err.close()

        self.server.close()


if __name__ == '__main__':
    server = Server()
    server.run()
