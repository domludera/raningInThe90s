import threading
import socket

from irc_user import IRCUser


class Client(threading.Thread):
    '''
    Multi-threading clients.
    '''

    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        pass

    def setup(self, __client, __address):
        self.ircuser = IRCUser()
        self.authenticated = False
        self.client = __client
        self.address = __address

    def isAuthenticated(self):
        return self.authenticated

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        while True:
            # print(self.client.__class__)
            data = self.client.recv(1024)
            print(data, self.client)
            if data:
                if not self.authenticated:
                    self.client.sendall(b'Enter username: ')
                    data = self.client.recv(1024)
                    self.ircuser.setUsername(str(data, 'utf-8').strip())
                    self.client.sendall(b'Enter nickname: ')
                    data = self.client.recv(1024)
                    self.ircuser.setNickname(str(data, 'utf-8').strip())
                    data = bytes(str(self.ircuser), 'utf-8')
                    self.client.sendall(data)
                    self.authenticated = self.ircuser.isAuthenticated()
                else:
                    self.client.sendall(data)
            else:
                print("Error:", self.address)
                self.client.close()


