#!/usr/bin/env python

import socket
import asyncore
import struct
import time

BIND_ADDR = ("", 7777)

HEADER_SIZE = 4

HEART_BEAT = 0

S2N_REGIST_PROXY_ASK = 1
N2S_REGIST_PROXY_RET = 2

C2N_REQUEST_PROXY_ASK = 3
N2C_REQUEST_PROXY_RET = 4

N2S_REQUEST_PROXY_ASK = 5
S2N_REQUEST_PROXY_RET = 6

S2N_RESPONSE_PROXY_ASK = 7
N2S_RESPONSE_PROXY_RET = 8

class NatConnector(asyncore.dispatcher):

    def __init__(self, mgr, name, sock, remote_addr):
        asyncore.dispatcher.__init__(self, sock)
        self.mgr = mgr
        self.name = name
        self.remote_addr = remote_addr
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.last_time = time.time()

    def handle_close(self):
        print self.name, " nat connector closed"
        self.close()
        self.mgr.on_connector_disconnect()

    def handle_error(self):
        print self.name, " nat connector error"
        self.handle_close()

    def handle_read(self):
        data = self.recv(2048)
        if not data:
            return
        self.recv_buffer += data
        while True:
            if len(self.recv_buffer) < HEADER_SIZE:
                break
            body_size, cmd = struct.unpack("!2H", self.recv_buffer[:HEADER_SIZE])
            if len(self.recv_buffer) < HEADER_SIZE + body_size:
                break
            body = self.recv_buffer[HEADER_SIZE:HEADER_SIZE+body_size]
            self.recv_buffer = self.recv_buffer[HEADER_SIZE+body_size:]

            if cmd == S2N_REGIST_PROXY_ASK:
                self.proxy_name = body
                self.mgr.on_regist_proxy(self.proxy_name, self)
            elif cmd == C2N_REQUEST_PROXY_ASK:
                proxy_name = body
                self.mgr.on_request_proxy(proxy_name, self)
            elif cmd == S2N_RESPONSE_PROXY_ASK:
                peer_name = body
                self.mgr.on_response_proxy(peer_name, self)

    def on_recv_data(self, data):
        self.send_buffer += data

    def writable(self):
        return len(self.send_buffer) > 0

    def handle_write(self):
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

    def get_name(self):
        return self.name

    def is_proxy(self):
        return self.proxy_name is not None

    def get_proxy_name(self):
        return self.proxy_name

    def get_remote_addr(self):
        return self.remote_addr

    def update(self):
        pass

class NatServer(asyncore.dispatcher):

    def __init__(self, bind_addr):
        asyncore.dispatcher.__init__(self)
        self.bind_addr = bind_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(bind_addr)
        self.listen(5)
        self.connectors = {}
        self.proxys = {}

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
            if connector.is_proxy():
                del self.proxys[connector.get_proxy_name()]
            connector.close()
        self.connectors[name] = NatConnector(self, name, sock, remote_addr)

    def on_connector_disconnect(self, name):
        connector = self.connectors.get(name)
        if connector is None:
            return
        if connector.is_proxy():
            del self.proxys[connector.get_proxy_name()]
        del self.connectors[name]

    def on_regist_proxy(self, proxy_name, connector):
        print "regist proxy:", proxy_name
        self.proxys[proxy_name] = connector

    def on_request_proxy(self, proxy_name, connector):
        proxy = self.proxys.get(proxy_name)
        if proxy is None:
            data = struct.pack("!2H", 0, N2C_REQUEST_PROXY_RET)
            connector.on_recv_data(data)
            return
        name = connector.get_name()
        data = struct.pack("!2H", len(name), N2S_REQUEST_PROXY_ASK) + name
        proxy.on_recv_data(data)

    def on_response_proxy(self, peer_name, connector):
        peer_connector = self.connectors.get(peer_name)
        if peer_connector is None:
            data = struct.pack("!2H", 0, N2S_RESPONSE_PROXY_RET)
            connector.on_recv_data(data)
            return
        addr = connector.get_remote_addr()
        body = addr[0] + ":" + str(addr[1])
        data = struct.pack("!2H", len(body), N2C_REQUEST_PROXY_RET) + body
        peer_connector.on_recv_data(data)
        addr = peer_connector.get_remote_addr()
        body = addr[0] + ":" + str(addr[1])
        data = struct.pack("!2H", len(body), N2S_RESPONSE_PROXY_RET) + body
        connector.on_recv_data(data)


    def update(self):
        for name in self.connectors:
            self.connectors[name].update()

serv = NatServer(BIND_ADDR)
while True:
    asyncore.loop(timeout = 1, count = 2)
    serv.update()
