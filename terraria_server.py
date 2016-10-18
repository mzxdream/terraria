#!/usr/bin/env python

import socket
import asyncore
import struct

t_host = ""
t_port = 7777
nat_host = ""
nat_port = 7777
header_size = 4

class NatClient(asyncore.dispatcher):

    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.status = 0
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.connect((nat_host, nat_port))
        self.buffer = bytes()

    def handle_connect(self):
        if self.status == 0:
            self.send(struct.pack("!2H", 0, 1))

    def handle_close(self):
        if self.status == 0:


    def handle_read(self):
        data = self.recv(2048)
        if not data:
            return
        self.buffer += data
