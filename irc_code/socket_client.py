import socket
import select
import errno
import sys
import time
import asyncio
import threading
import patterns


class SocketClient(threading.Thread, patterns.Publisher):

    def __init__(self, HOST, PORT):
        super().__init__(daemon=True)
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.HOST, self.PORT))
        self.msg = b''
        self.inputs = [self.s]
        self.outputs = []
        self.irc = None
        self.username = ''

    def set_irc(self, irc):
        self.irc = irc

    def set_irc_username(self, username):
        self.irc.username = username

    def update(self, msg):
        self.irc.view.add_msg(self.username, msg)

    def handleRead(self, read):
        for s in read:
            try:
                data = self.s.recv(1024)
                if data:
                    if self.irc:
                        self.update(str(data, 'utf-8'))
                    if s not in self.outputs:
                        self.outputs.append(s)
            except socket.error as e:
                if e.errno == errno.ECONNRESET:
                    data = None
                else:
                    raise e

    def handleWrite(self, write):
        for s in write:
            if self.msg:
                self.s.send(self.msg)
                if self.irc:
                    if not self.irc.username:
                        self.username = str(self.msg, 'utf-8')
                        self.set_irc_username(self.username)
                self.outputs.remove(s)
        self.msg = b''

    def run(self):
        while 1:
            read, write, err = self.get_ready_sockets()
            self.handleRead(read)
            self.handleWrite(write)

    def get_ready_sockets(self):
        return select.select(self.inputs, self.outputs, self.inputs)

    def setMsg(self, msg):
        self.msg = bytes(msg, 'utf-8')


