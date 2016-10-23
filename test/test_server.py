#!/usr/bin/env python

import socket
import asyncore

BIND_ADDR = ("", 7777)

class Client(asyncore.dispatcher):

    def __init__(self, sock, remote_addr):
        asyncore.dispatcher.__init__(self, sock)
        self.remote_addr = remote_addr
        self.send_buffer = bytes()

    def handle_read(self):
        data = self.recv(2048)
        if not data:
            return
        print self.remote_addr, "->", data
        self.send_buffer += data

    def writable(self):
        return len(self.send_buffer) > 0

    def handle_write(self):
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]


class Server(asyncore.dispatcher):

    def __init__(self, bind_addr):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(bind_addr)
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            Client(sock, addr)


serv = Server(BIND_ADDR)

asyncore.loop()
