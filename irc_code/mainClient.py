#!/bin/python3
from socket_client import SocketClient

socket = SocketClient('localhost', 50012)
socket.run()
