#!/usr/bin/env python

import socket
import asyncore
import struct
import time

local_host = ""
local_port = 4566
serv_name = "mzx"

dest_host = ""
dest_port = 7777

nat_host = ""
nat_port = 7777

header_size = 4

HEART_BEAT = 0

S2N_REGISTE_SERV_ASK = 1
N2S_REGISTE_SERV_RET = 2

N2S_CLIENT_CONNECT_ASK = 3
S2N_CLIENT_CONNECT_RET = 4

S2N_CONNECT_CLIENT_ASK = 5
N2S_CONNECT_CLIENT_RET = 6

class ProxyLocalClient(asyncore.dispatcher):
    pass

class ProxyRemoteClient(asyncore.dispatcher):
    def __init__(self, handler, key):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("", 0))
        self.connect((nat_host, nat_port))
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.status = "connecting"
        self.connect_client = False
        self.last_time = time.time()
        self.handler = handler
        self.key = key
        self.client_addr = None
        self.client = None

    def handle_connect(self):
        self.status = "connected"
        self.last_time = time.time()
        if not self.connect_client:
            cmd = S2N_CONNECT_CLIENT_ASK
            self.send_buffer += (struct.pack("!2H", len(self.key), cmd) + self.key)
            print "connect nat server"
        else:
            if self.client:
                self.client.close()
            self.client = ProxyLocalClient(self)
            self.send_buffer = bytes()
            self.recv_buffer = bytes()

    def handle_close(self):
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.status = "disconnect"
        self.last_time = time.time()

    def handle_error(self):
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.status = "disconnect"
        self.last_time = time.time()

    def reconnect(self):
        if not self.connect_client:
            self.connect((nat_host, nat_port))
        else:
            self.connect((self.client_addr, self.clent_port))
        self.status = "connecting"


    def handle_read(self):
        self.last_time = time.time()
        data = self.recv(2048)
        if not data:
            return
        self.recv_buffer += data
        self.handle_package()

    def handle_write(self):
        self.last_time = time.time()
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

    def writable(self):
        return self.status != "connected" or len(self.send_buffer) > 0

    def handle_package(self):
        while True:
            if len(self.send_buffer) < header_size:
                break
            body_size, cmd = struct.unpack("!2H", self.send_buffer[:header_size])
            if len(self.send_buffer) < header_size + body_size:
                break
            body = self.send_buffer[header_size:header_size+body_size]
            self.send_buffer = self.send_buffer[header_size+body_size:]
            self.handle_cmd(cmd, body)

    def handle_cmd(self, cmd, body):
        if not self.connect_client:
            if cmd == N2S_CONNECT_CLIENT_RET:
                addr = body.split(":")
                if addr != 2:
                    self.close()
                    self.handler.close_connect(self.key)
                    return
                self.client_addr = (addr[0], int(addr[1]))
                addr = self.socket.getsockname()
                self.close()



    def handle_new_connect(self, key):
        self.clients[key] = ProxyRemoteClient(self, key)

    def close_connect(self, key):
        del self.clients[key]


    def update(self):
        if time.time() - self.last_time > 10:
            if self.status == "disconnect":
                self.reconnect()
            elif self.status == "connected":
                cmd = HEART_BEAT
                self.send_buffer += struct.pack("!2H", 0, cmd)
        self.last_time = time.time()
        for key in self.clients:
            self.clients[key].update()

    pass

class NatClient(asyncore.dispatcher):

    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((nat_host, nat_port))
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.status = "connecting"
        self.clients = {}
        self.last_time = time.time()

    def handle_connect(self):
        self.status = "connected"
        body = serv_name.encode()
        cmd = G2N_REGISTE_ASK
        self.send_buffer += (struct.pack("!2H", len(body), cmd) + body)
        self.last_time = time.time()
        print "connect server"

    def handle_close(self):
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.status = "disconnect"
        self.last_time = time.time()

    def handle_error(self):
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.status = "disconnect"
        self.last_time = time.time()

    def reconnect(self):
        self.connect((nat_host, nat_port))
        self.status = "connecting"


    def handle_read(self):
        self.last_time = time.time()
        data = self.recv(2048)
        if not data:
            return
        self.recv_buffer += data
        self.handle_package()

    def handle_write(self):
        self.last_time = time.time()
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

    def writable(self):
        return self.status != "connected" or len(self.send_buffer) > 0

    def handle_package(self):
        while True:
            if len(self.send_buffer) < header_size:
                break
            body_size, cmd = struct.unpack("!2H", self.send_buffer[:header_size])
            if len(self.send_buffer) < header_size + body_size:
                break
            body = self.send_buffer[header_size:header_size+body_size]
            self.send_buffer = self.send_buffer[header_size+body_size:]
            self.handle_cmd(cmd, body)

    def handle_cmd(self, cmd, body):
        if cmd == N2G_CONNECT_ASK:
            self.handle_new_connect(body)

    def handle_new_connect(self, key):
        self.clients[key] = ProxyRemoteClient()


    def update(self):
        if time.time() - self.last_time > 10:
            if self.status == "disconnect":
                self.reconnect()
            elif self.status == "connected":
                cmd = HEART_BEAT
                self.send_buffer += struct.pack("!2H", 0, cmd)
        self.last_time = time.time()
        for key in self.clients:
            self.clients[key].update()

handler = NatClient()

while True:
    asyncore.loop(5)
    handler.update()
