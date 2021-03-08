import threading
import socket

import sys, errno

from irc_user import IRCUser


class ServerThread(threading.Thread):
    '''
    Multi-threading clients.
    '''

    def __init__(self):
        threading.Thread.__init__(self)
        pass

    def setup(self, __client, __address, server_instance):
        self.ircuser = IRCUser()
        self.authenticated = False
        self.joinedChannel = False
        self.client = __client
        self.address = __address
        self.server_instance = server_instance

    def isAuthenticated(self):
        return self.authenticated

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        b = True
        while b:
            # print(self.client)
            try:
                if not self.authenticated:
                    self.authenticate()

                elif not self.joinedChannel:
                    self.joinChannel()

            except IOError as e:
                if e.errno == errno.EPIPE:
                    print('IO Error', self.client)
                    b = False

    def authenticate(self):
        self.client.send(b'Enter username:')
        data = self.client.recv(1024)
        self.ircuser.setUsername(str(data, 'utf-8').strip())
        self.client.send(b'Enter nickname:')
        data = self.client.recv(1024)
        self.ircuser.setNickname(str(data, 'utf-8').strip())
        self.authenticated = self.ircuser.isAuthenticated()
        if self.authenticated:
            resp = 'Welcome ' + self.ircuser.getNickname() + '! -- User authenticated'
            self.client.send(bytes(resp, 'utf-8'))
        else:
            self.client.send(b'User authentication failed!')

    def joinChannel(self):
        self.ircuser.joinChannel('#global')
        self.joinedChannel = self.ircuser.joinedChannel()
        resp = 'Joined channel ' + self.ircuser.getChannel()
        self.client.send(bytes(resp, 'utf-8'))
