#!/bin/python3
import socket
import sys
import select
import errno
import queue

from threading import Thread

from irc_user import IRCUser

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
        self.ircusers = dict()
        self.readers = []
        self.writers = []

    def initUser(self, sock):
        sock.send(b'Welcome!\n')
        self.ircusers[sock] = IRCUser()

    def getUsername(self, sock):
        sock.send(b'Enter your username: ')

    def setUsername(self, sock, data):
        self.ircusers[sock].setUsername(str(data, 'utf-8'))
        print('username set to: ', str(self.ircusers[sock].getUsername()))

    def getNickname(self, sock):
        sock.send(b'Enter your nickname: ')

    def setNickname(self, sock, data):
        self.ircusers[sock].setNickname(str(data, 'utf-8'))
        print('nickname set to: ', str(self.ircusers[sock].getNickname()))

    def acceptNewConnection(self):
        client, addr = self._s.accept()

        client.setblocking(0)
        self.readers.append(client)
        print('Connected: ', len(self.readers)-1)

    def joinChannel(self, sock, channel):
        self.ircusers[sock].joinChannel(channel)
        print('joined channel: ', str(self.ircusers[sock].getChannel()))


    def handleReader(self, read, data):
        for sock in read:
            if sock is self._s:
                self.acceptNewConnection()
            else:
                try:
                    data = sock.recv(self.recv_bytes)
                except socket.error as e:
                    if e.errno ==errno.ECONNRESET:
                        data = None
                    else:
                        raise e
                if data:
                    if sock not in self.ircusers:
                        self.initUser(sock)
                        if sock not in self.writers:
                            self.writers.append(sock)
                    if not self.ircusers[sock].isAuthenticated():
                        if not self.ircusers[sock].getUsername():
                            self.getUsername(sock)
                        elif not self.ircusers[sock].getNickname():
                            self.getNickname(sock)
                    else:
                        self.joinChannel(sock, '#global')
                    return data
                else:
                    # if we received 0 byte, then nuke the socket
                    if sock in self.writers:
                        self.writers.remove(sock)
                    self.readers.remove(sock)
                    sock.close()

    def handleWriter(self, write, data):
        for sock in write:
            if data:
                if not self.ircusers[sock].isAuthenticated():
                    if not self.ircusers[sock].getUsername():
                        self.setUsername(sock, data)
                    elif not self.ircusers[sock].getNickname():
                        self.setNickname(sock, data)

                #if self.sender is not sock: # MAYBE REMOVE
                #    try:
                #        sock.send(data)
                #    except socket.error as e:
                #        if sock in self.writers:
                #            self.writers.remove(sock)

    def handleError(self, err, data):
        for sock in err:
            self.readers.remove(sock)
            if sock in self.writers:
                self.writers.remove(sock)
            sock.close()

    def run(self):
        print('Server started on', self.HOST, self.PORT)
        self._s.listen()
        self.readers.append(self._s)
        mainloop = Thread(self.mainServerLoop())
        mainloop.start()


    def mainServerLoop(self):
        data = None
        # main server loop
        while self.readers:
            # used for non blocking sockets - ready to: write, read, error
            read, write, err = select.select(self.readers, self.writers, self.readers)

            data = self.handleReader(read, data)
            self.handleWriter(write, data)
            self.handleError(err, data)

