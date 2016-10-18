#!/usr/bin/env python

import socket
import asyncore
import struct

host = ""
port = 7777
header_size = 4

servers = []

class NatClient(asyncore.dispatcher_with_send):

    def __init__(self, sock, addr):
        asyncore.dispatcher_with_send.__init__(sock)
        self.addr = addr
        self.buffer = bytes()

    def handle_read(self):
        data = self.recv(2048)
        if not data:
            return
        self.buffer += data
        while True:
            if len(self.buffer) < header_size:
                break
            body_size, cmd = struct.unpack("!2H", self.buffer[:header_size])
            if len(self.buffer) < header_size + body_size:
                break
            body = self.buffer[header_size:header_size+body_size]
            self.buffer = self.buffer[header_size+body_size]
            self.handle_cmd(cmd, body)

    def handle_close(self):
        servers.remove(self)

    def handle_error(self):
        servers.remove(self)

    def handle_cmd(self, cmd, body):
        if cmd == 1:
            if self not in servers:
                servers.append(self)
                print self.addr, "is server"
        elif cmd == 2:
            if len(servers) <= 0:
                self.send(struct.pack("!2H", 0, 2))
                print self.addr, " get no server"
            else:
                server = servers[0]
                del servers[0]
                body = (server.addr[0] + ":" + str(server.addr[1])).encode()
                self.send(struct.pack("!2H", len(body), 3) + body)
                body = (self.addr[0] + ":" + str(self.addr[1])).encode()
                server.send(struct.pack("!2H", len(body), 4) + body)
                print self.addr, "connect to", server.addr


class NatServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print addr, "is connect"
            NatClient(sock, addr)

    def handle_error(self):
        pass

NatServer(host, port)
asyncore.loop()
