import threading
import socket

import sys, errno

import re

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
        self.client.send(b'Please authenticate using IRC commands')
        while b:
            # print(self.client)
            try:
                if not self.authenticated:
                    # self.authenticate()
                    data = self.client.recv(1024)
                    re_user = re.compile('USER\W(\S+)')
                    m = re_user.match(str(data, 'utf-8'))
                    if m:
                        self.ircuser.setUsername(m.group(1))
                        resp = 'Username set to ' + self.ircuser.getUsername()
                        self.client.send(bytes(resp, 'utf-8'))
                    re_nick = re.compile('NICK\W(\S+)')
                    m = re_nick.match(str(data, 'utf-8'))
                    if m:
                        self.ircuser.setNickname(m.group(1))
                        resp = 'Nickname set to ' + self.ircuser.getNickname()
                        self.client.send(bytes(resp, 'utf-8'))
                        self.authenticate()

            except IOError as e:
                if e.errno == errno.EPIPE:
                    print('IO Error', self.client)
                    b = False

    def authenticate(self):
        # self.client.send(b'Enter username:')
        # data = self.client.recv(1024)
        # self.ircuser.setUsername(str(data, 'utf-8').strip())
        # self.client.send(b'Enter nickname:')
        # data = self.client.recv(1024)
        # self.ircuser.setNickname(str(data, 'utf-8').strip())
        self.authenticated = self.ircuser.isAuthenticated()
        resp = 'Welcome ' + self.ircuser.getNickname() + '! -- User authenticated '
        self.client.send(bytes(resp, 'utf-8'))
        self.joinChannel()

    def joinChannel(self):
        self.ircuser.joinChannel('#global')
        self.joinedChannel = self.ircuser.joinedChannel()
        resp = 'Joined channel ' + self.ircuser.getChannel()
        self.client.send(bytes(resp, 'utf-8'))
