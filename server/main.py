#!/bin/python3
from server import Server

server = Server()
try:
    server.run()
except KeyboardInterrupt:
    print('DISCONNECTED SERVER')

