#!/bin/python3
from chatserver import ChatServer
from threading import Thread

# server = ChatServer()
# server.run()

from Server import Server
from Client import Client

server = Server()
server.run()

