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

        self.inputs = [self.server]
        self.outputs = []
        self.clients = dict()

        self.sender = None
        self.data = b''

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

    def handler_reader(self, inready):
        for s in inready:

            if s == self.server:
                sock, address = self.server.accept();
                server_thread = ServerThread()
                server_thread.setup(sock, address, self, self.logger)
                try:
                    server_thread.start()
                except KeyboardInterrupt:
                    server_thread.join()
                self.clients[server_thread.client] = server_thread
                self.outputs.append(server_thread.client)
            else:
                try:
                    data = s.recv(1024)

                    loud_mouth = self.clients[s]
                    self.logger.debug('Received data: %s, from: %s', data.decode('utf-8'),
                                      loud_mouth.ircuser.getNickname())
                    if data:
                        self.sender = s
                        self.data = data
                        if s not in self.outputs:
                            self.outputs.append(s)
                    else:
                        loud_mouth = self.clients[s].ircuser.getNickname()
                        if loud_mouth:
                            self.logger.debug('%s %s has disconnected', s, loud_mouth)
                        self.inputs.remove(s)
                        self.outputs.remove(s)
                        del self.clients[s]
                        s.close()
                except socket.error as e:
                    if e.errno == errno.ECONNRESET:
                        data = None
                    else:
                        raise e

    def handle_writer(self, outready):
        for s in outready:
            if s.fileno() > 0:
                if self.clients[s].joinedChannel:
                    if self.data:
                        self.send_resp(s)
                    if s not in self.inputs:
                        self.inputs.append(s)
            else:
                if s in self.outputs:
                    self.outputs.remove(s)
        self.data = b''

    def handle_err(self, excready):
        for err in excready:
            self.inputs.remove(err)
            self.outputs.remove(err)
            # del self.clients[err]
            err.close()

    def run(self):
        self.logger.debug('Server running, listening for inbound connections')
        self.server.listen()
        
        while True:

            inready, outready, excready = select.select(self.inputs, self.outputs, self.inputs)

            self.handler_reader(inready)
            self.handle_writer(outready)
            self.handle_err(excready)

    def send_resp(self, s):
        sender = self.clients[self.sender].ircuser.getNickname()
        msg = sender + '~' + str(self.data, 'utf-8')
        s.sendall(bytes(msg, 'utf-8'))


if __name__ == '__main__':
    server = Server()
    server.run()
