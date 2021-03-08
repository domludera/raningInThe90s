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

    def set_irc(self, irc):
        self.irc = irc

    def update(self, msg):
        self.irc.update(msg)

    def handleRead(self, read):
        for s in read:
            try:
                data = self.s.recv(1024)
                if data:
                    if self.irc:
                        self.update(str(data, 'utf-8'))
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
                self.outputs.remove(s)
        self.msg = b''

    def run(self):
        self.s.send(b'\n')
        while 1:
            read, write, err = self.getReadySockets()
            self.handleRead(read)
            self.handleWrite(write)

    def getReadySockets(self):
        return select.select(self.inputs, self.outputs, self.inputs)

    def setMsg(self, msg):
        self.msg = bytes(msg, 'utf-8')


