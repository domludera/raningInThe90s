import errno
import select
import socket
import logging



from server_thread import ServerThread

class Server(object):
    '''
    Threading server
    '''

    def __init__(self):
        '''
        Constructor
        '''
        SERVER = 'localhost'
        PORT = 50012

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER, PORT))
        self.sender = None

        # logger setup
        logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=('debug.log'))

        self.logger = logging.getLogger()
        self.handler = logging.StreamHandler()
        self.formatter = logging.Formatter(
                '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

        self.logger.debug('Logger initialized for server "%s" at port %s', SERVER, PORT)

    def run(self):
        self.logger.debug('Server running, listening for inbound connections')
        self.server.listen()
        
        inputs = [self.server]
        outputs = []
        clients = dict()

        while True:

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
                            self.logger.debug('Received data: %s', data.decode('utf-8'))
                        except socket.error as e:
                            if e.errno == errno.ECONNRESET:
                                data = None
                            else:
                                raise e
                        if data:
                            self.sender = s
                            self.msg = data
                            for c in outready:
                                if c is not self.sender:
                                    if clients[c].joinedChannel:
                                        c.sendall(data)
                        else:
                            #nicholas = serverThread.ircuser.getNickname()
                            self.logger.debug('%s has disconnected', s) # nicholas?
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
