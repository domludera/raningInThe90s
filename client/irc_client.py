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
import logging

import patterns
import view

from themesong import ThemeSong

import sys, getopt

from socket_client import SocketClient

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()


class IRCClient(patterns.Subscriber):

    def __init__(self, HOST, PORT, music):
        super().__init__()
        self.username = str()
        self._run = True
        self._s = SocketClient(HOST, PORT)
        self._s.set_irc(self)
        self.music = music

    def set_view(self, view):
        self.view = view

    def set_username(self, username):
        self.username = username

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
        self._s.start()

    def close(self):
        # Terminate connection
        logger.debug(f"Closing IRC Client object")
        pass


def get_help_menu():
    menu = """usage: irc_client.py [-h] [--server '<SERVER>' --port '<PORT>'] [-m]

optional arguments:
    -h, --help              Show this help message and exit
    --server '<SERVER>'     Target server to initiate a connection to
    --port <PORT>           Target port to use
    -m                      Enable music
        """
    return menu


def init_client(cmdargs):
    HOST = ''
    PORT = 0
    music = False
    try:
        opts, arguments = getopt.getopt(cmdargs, "hms:p:", ["help", "server=", "port="])
    except getopt.GetoptError:
        print(get_help_menu())
        sys.exit(2)
    for opt, arg in opts:
        if opt != '-h' or opt != '--help':
            if opt == '--server':
                HOST = arg
            if opt == '--port':
                PORT = arg
            if opt == '-m':
                music = True
        else:
            print(get_help_menu())
            sys.exit()
    if len(opts) < 1:
        print(get_help_menu())
        sys.exit()

    return IRCClient(HOST, int(PORT), music)


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

        if client.music:
            music_thread = ThemeSong()
            music_thread.start()

        async def inner_run():
            await asyncio.gather(
                v.run(),
                client.run(),
                return_exceptions=True,
            )
        try:
            asyncio.run(inner_run())
        except KeyboardInterrupt as e:
            music_thread.stop()
            music_thread.join()
            logger.debug(f"Signifies end of process")
    client.close()


if __name__ == "__main__":
    # Parse your command line arguments here
    args = None
    main(sys.argv[1:])
