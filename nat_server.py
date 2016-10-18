#!/usr/bin/env python

import socket
import asyncore

host = ""
port = 11111


class NatServer(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)

