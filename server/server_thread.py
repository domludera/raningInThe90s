import threading
import socket
import re

import sys
import errno

import re

from irc_user import IRCUser


class ServerThread(threading.Thread):
    '''
    Multi-threading clients.
    '''

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        pass

    def setup(self, __client, __address, server_instance, logger):
        self.ircuser = IRCUser()
        self.authenticated = False
        self.joinedChannel = False
        self.client = __client
        self.address = __address
        self.server_instance = server_instance
        self.logger = logger

    def isAuthenticated(self):
        return self.authenticated

    # def connect(self):
    #     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        b = True
        re_user = re.compile('(USER)\W(\S+)')
        re_nick = re.compile('(NICK)\W(\S+)')
        self.send_resp('STANDARD IRC CONFIG COMMANDS, please set your username and nickname using USER and '
                              'NICK command\n USER <username>\n NICK <nickname>')

        try:
            while not self.authenticated:
                try:
                    data = self.client.recv(1024)
                    if data:

                        m_user = re_user.match(str(data, 'utf-8'))
                        m_nick = re_nick.match(str(data, 'utf-8'))
                        if m_user:
                            self.ircuser.setUsername(m_user.group(2))
                            resp = 'USER set to ' + self.ircuser.getUsername()
                            self.send_resp(resp)
                        elif m_nick:
                            self.ircuser.setNickname(m_nick.group(2))
                            resp = 'NICK set to ' + self.ircuser.getNickname()
                            self.send_resp(resp)

                        if not self.ircuser.getUsername():
                            self.send_resp('Please set your username first using USER <username>')
                        elif not self.ircuser.getNickname():
                            self.send_resp('Please set your nickname using NICK <nickname>')
                        else:
                            self.authenticate()

                    else:
                        self.logger.debug('%s has disconnected', self.client)
                        break

                except IOError as e:
                    if e.errno == errno.EPIPE:
                        print('IO Error', self.client)
                        b = False
        except KeyboardInterrupt:
            self.join()

        self.joinChannel()

    def authenticate(self):
        self.authenticated = self.ircuser.isAuthenticated()
        if self.authenticated:
            resp = 'Welcome ' + self.ircuser.getNickname() + '! -- User authenticated -- '
            self.send_resp(resp)

    def joinChannel(self):
        self.ircuser.joinChannel('#global')
        self.joinedChannel = self.ircuser.joinedChannel()
        resp = 'Joined channel ' + self.ircuser.getChannel()
        self.send_resp(resp)

    def send_resp(self, msg):
        resp = 'client~'+msg
        self.client.send(bytes(resp, 'utf-8'))
