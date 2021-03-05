#!/bin/python3
import socket
import sys
import select
import errno
import queue

class ChatServer:

    def __init__(self):

        self.HOST = 'localhost'
        self.PORT = 50011
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._s.bind((self.HOST, self.PORT))
        self._s.setblocking(0) # bonus
        self.recv_bytes = 1024
        self.data = '' # current data to be broadcasted
        self.sender = None # who is the sender of the above data

    def run(self):
        print('Server started on', self.HOST, self.PORT)
        self._s.listen()
        readers = [self._s]
        writers = []

        queues = dict()
        # main server loop
        while readers:
            # used for non blocking sockets - ready to: write, read, error
            read, write, err = select.select(readers, writers, readers)


            for sock in read:
                if sock is self._s:
                    client, addr = self._s.accept()
                    print(client, addr)
                    client.setblocking(0)
                    readers.append(client)
                    queues[client] = queue.Queue()
                    print('Connected: ', len(readers))
                else:
                    try:
                        self.data = sock.recv(self.recv_bytes)
                        print(self.data) # debugging
                        self.sender = sock
                    except socket.error as e:
                        if e.errno ==errno.ECONNRESET:
                            self.data = None
                        else:
                            raise e
                    if self.data:
                        queues[sock].put(self.data)
                        if sock not in writers:
                            writers.append(sock)
                    else:
                        # if we received 0 byte, then nuke the socket
                        if sock in writers:
                            writers.remove(sock)
                        readers.remove(sock)
                        sock.close()
            for sock in write:
                if self.data:
                    if self.sender is not sock: # MAYBE REMOVE
                        try:
                            sock.send(self.data)
                        except socket.error as e:
                            if sock in writers:
                                writers.remove(sock)
            for sock in err:
                readers.remove(sock)
                if sock in writers:
                    writers.remove(sock)
                sock.close()
            self.data = ''
