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

    def setup(self, __client, __address):
        self.ircuser = IRCUser()
        self.authenticated = False
        self.joinedChannel = False
        self.client = __client
        self.address = __address

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
                if not self.joinedChannel:
                    self.joinChannel()
            except IOError as e:
                if e.errno == errno.EPIPE:
                    print('IO Error', self.client)
                    b = False
            # else:
            #     print("Error:", self.address)
            #     self.client.close()

    def authenticate(self):
        self.client.sendall(b'Enter username: \n')
        data = self.client.recv(1024)
        print(data)
        self.ircuser.setUsername(str(data, 'utf-8').strip())
        self.client.sendall(b'Enter nickname: \n')
        data = self.client.recv(1024)
        print(data)
        self.ircuser.setNickname(str(data, 'utf-8').strip())
        self.authenticated = self.ircuser.isAuthenticated()
        if self.authenticated:
            resp = 'Welcome ' + self.ircuser.getNickname() + '! -- User authenticated\n'
            self.client.sendall(bytes(resp, 'utf-8'))
        else:
            self.client.sendall(b'User authentication failed!\n')

    def joinChannel(self):
        self.client.sendall(b'Enter channel to join: ')
        data = self.client.recv(1024)
        self.ircuser.joinChannel(str(data, 'utf-8').strip())
        self.joinedChannel = self.ircuser.joinedChannel()
        if self.joinedChannel:
            resp = 'Joined channel ' + self.ircuser.getChannel() + '\n'
            self.client.sendall(bytes(resp, 'utf-8'))
        else:
            self.client.sendall(b'Failed to join channel!\n')
