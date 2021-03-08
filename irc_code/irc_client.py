#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021
#
# Distributed under terms of the MIT license.

"""
Description:

"""
import asyncio
import concurrent
import logging

import patterns
import view

import sys, getopt
from concurrent.futures import Future, ThreadPoolExecutor

from socket_client import SocketClient

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()


class IRCClient(patterns.Subscriber):

    def __init__(self, HOST, PORT):
        super().__init__()
        self.username = str()
        self._run = True
        self._s = SocketClient(HOST, PORT)

    def set_view(self, view):
        self.view = view

    def update(self, msg):
        # TODO Will need to modify this
        if not isinstance(msg, str):
            raise TypeError(f"Update argument needs to be a string")
        elif not len(msg):
            # Empty string
            return
        logger.info(f"IRCClient.update -> msg: {msg}")
        self.process_input(msg)

    def process_input(self, msg):
        # TODO Will need to modify this
        self.add_msg(msg)
        self._s.setMsg(msg)

        if msg.lower().startswith('/quit'):
            # Command that leads to the closure of the process
            raise KeyboardInterrupt

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    async def run(self):
        """
        Driver of your IRC Client
        """
        self.add_msg('Welcome!')
        self._s.start()

    def close(self):
        # Terminate connection
        logger.debug(f"Closing IRC Client object")
        pass


def get_help_menu():
    menu = """usage: irc_client.py [-h] [--server SERVER] [--port PORT]

optional arguments:
    -h, --help         Show this help message and exit
    --server SERVER    Target server to initiate a connection to
    --port PORT        Target port to use
        """
    return menu


def init_client(cmdargs):
    HOST = ''
    PORT = 0
    try:
        opts, arguments = getopt.getopt(cmdargs, "hs:p:", ["help", "server=", "port="])
    except getopt.GetoptError:
        print(get_help_menu())
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h' or opt == '--help':
            print(get_help_menu())
            sys.exit()
        if opt == '--server':
            HOST = arg
        if opt == '--port':
            PORT = arg
    return IRCClient(HOST, int(PORT))


def main(args):
    # Pass your arguments where necessary
    client = init_client(args)
    logger.info(f"Client object created")
    with view.View() as v:
        logger.info(f"Entered the context of a View object")
        client.set_view(v)
        logger.debug(f"Passed View object to IRC Client")
        v.add_subscriber(client)
        logger.debug(f"IRC Client is subscribed to the View (to receive user input)")

        async def inner_run():
            await asyncio.gather(
                v.run(),
                client.run(),
                return_exceptions=True,
            )
        try:
            asyncio.run(inner_run())
        except KeyboardInterrupt as e:
            logger.debug(f"Signifies end of process")
    client.close()


if __name__ == "__main__":
    # Parse your command line arguments here
    args = None
    main(sys.argv[1:])
