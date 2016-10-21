#!/usr/bin/env python

import socket
import asyncore
import struct
import time

BIND_ADDR = ("", 7777)

HEADER_SIZE = 4

HEART_BEAT = 0

S2N_REGIST_SERV_ASK = 1
N2S_REGIST_SERV_RET = 2

C2N_REQUEST_PROXY_ASK = 3
N2C_REQUEST_PROXY_RET = 4

N2S_REQUEST_PROXY_ASK = 5
S2N_REQUEST_PROXY_RET = 6

S2N_REGIST_PROXY_ASK = 7
N2S_REGIST_PROXY_RET = 8

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
            if len(self.buffer) < HEADER_SIZE:
                break
            body_size, cmd = struct.unpack("!2H", self.buffer[:HEADER_SIZE])
            if len(self.buffer) < HEADER_SIZE + body_size:
                break
            body = self.buffer[HEADER_SIZE:HEADER_SIZE+body_size]
            self.buffer = self.buffer[HEADER_SIZE+body_size]
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

    def __init__(self, bind_addr):
        asyncore.dispatcher.__init__(self)
        self.bind_addr = bind_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(bind_addr)
        self.listen(5)
        self.connectors = {}
        self.servers = {}

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            self.create_new_connector(sock, addr)

    def handle_error(self):
        print "nat server error"

    def create_new_connector(self, sock, remote_addr):
        name = str(sock.fileno())
        connector = self.connectors.get(name)
        if connector is not None:
            connecotr.clear()
        self.connectors[name] = NatConnector(self, name, sock, remote_addr)

    def on_connector_disconnect(self, name):
        del self.connectors[name]


serv = NatServer(bind_addr)
while True:
    asyncore.loop(timeout = 1, count = 2)
    serv.update()
