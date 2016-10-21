#!/usr/bin/env python

import socket
import asyncore
import struct
import time

SERV_NAME = "mzx"
PROXY_ADDR = ("", 7777)
NAT_ADDR = ("", 7777)

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

class LocalProxy(asyncore.dispatcher):

    def __init__(self, mgr, remote_addr):
        asyncore.dispatcher.__init__(self)
        self.mgr = mgr
        self.remote_addr = remote_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect(self.remote_addr)
        self.last_time = time.time()
        self.connect_count = 1
        self.status = "connecting"
        self.send_buffer = bytes()

    def handle_connect(self):
        self.status = "connected"

    def handle_close(self):
        self.close()
        if self.status == "connected":
            self.mgr.on_local_disconnect()
            return
        self.status = "disconnect"

    def handle_error(self):
        self.handle_close()

    def handle_read(self):
        data = self.recv(2048)
        if not data:
            return
        self.mgr.on_local_recv(data)

    def on_recv_data(self, data):
        self.send_buffer += data

    def writable(self):
        return self.status != "connected" or len(self.send_buffer) > 0

    def handle_write(self):
        if len(self.send_buffer) <= 0:
            return
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

    def reconnect(self):
        if self.connet_count > 10:
            self.handle_close()
            return
        self.status = "connecting"
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect(self.remote_addr)
        self.last_time = time.time()
        self.connect_count += 1

    def update(self):
        now_time = time.time()
        if self.status == "disconnect":
            if now_time >= self.last_time + 2 ** self.connet_count:
                self.reconnect()

class RemoteProxy(asyncore.dispatcher):

    def __init__(self, mgr, bind_addr, remote_addr):
        asyncore.dispatcher.__init__(self)
        self.mgr = mgr
        self.bind_addr = bind_addr
        self.remote_addr = remote_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(self.bind_addr)
        self.connect(self.remote_addr)
        self.last_time = time.time()
        self.connect_count = 1
        self.status = "connecting"
        self.send_buffer = bytes()

    def handle_connect(self):
        self.status = "connected"

    def handle_close(self):
        print "remote proxy close"
        self.close()
        if self.status == "connected":
            self.mgr.on_remote_disconnect()
            return
        self.status = "disconnect"

    def handle_error(self):
        self.handle_close()

    def handle_read(self):
        data = self.recv(2048)
        if not data:
            return
        self.mgr.on_remote_recv(data)

    def on_recv_data(self, data):
        self.send_buffer += data

    def writable(self):
        return self.status == "connecting" or len(self.send_buffer) > 0

    def handle_write(self):
        if len(self.send_buffer) <= 0:
            return
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

    def reconnect(self):
        if self.connet_count > 10:
            self.handle_close()
            return
        self.status = "connecting"
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(self.bind_addr)
        self.connect(self.remote_addr)
        self.last_time = time.time()
        self.connect_count += 1

    def update(self):
        now_time = time.time()
        if self.status == "disconnect":
            if now_time >= self.last_time + 2 ** self.connet_count:
                self.reconnect()

class ProxyHelper(asyncore.dispatcher):

    def __init__(self, mgr, name, remote_addr):
        asyncore.dispatcher.__init__(self)
        self.mgr = mgr
        self.name = name
        self.remote_addr = remote_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect(self.remote_addr)
        self.last_time = time.time()
        self.connect_count = 1
        self.status = "connecting"

    def handle_connect(self):
        self.status = "connected"
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.send_buffer += (struct.pack("!2H", len(self.name), S2N_REGIST_PROXY_ASK) + self.name)

    def handle_close(self):
        print self.name, "helper server close"
        self.close()
        if self.status == "connected":
            self.mgr.on_helper_disconnect()
            return
        self.status = "disconnect"

    def handle_error(self):
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

            if cmd == N2S_REGIST_PROXY_RET:
                addr = body.split(":")
                if len(addr) != 2:
                    self.handle_close()
                    print "help proxy recv:", body
                    return
                bind_addr = self.socket.getsockname()
                remote_addr = (addr[0], int(addr[1]))
                self.close()
                self.mgr.on_helper_proxy(bind_addr, remote_addr)
                return

    def writable(self):
        return self.status == "connecting" or len(self.send_buffer) > 0

    def handle_write(self):
        if len(self.send_buffer) <= 0:
            return
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

    def reconnect(self):
        if self.connet_count > 10:
            self.handle_close()
            return
        self.status = "connecting"
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect(self.remote_addr)
        self.last_time = time.time()
        self.connect_count += 1

    def update(self):
        now_time = time.time()
        if self.status == "disconnect":
            if now_time >= self.last_time + 2 ** self.connet_count:
                self.reconnect()

class ProxyManager():
    def __init__(self, mgr, name, proxy_addr, remote_addr):
        self.mgr = mgr
        self.name = name
        self.proxy_addr = proxy_addr
        self.remote_addr = remote_addr
        self.proxy_helper = ProxyHelper(self, name, remote_addr)

    def on_helper_disconnect(self):
        print "helper:", self.name, "disconnect"
        self.clear()
        self.mgr.on_proxy_disconnect(self.name)

    def on_remote_disconnect(self):
        print "remote:", self.name, "disconnect"
        self.clear()
        self.mgr.on_proxy_disconnect(self.name)

    def on_local_disconnect(self):
        print "connect:", self.name, "disconnect"
        self.clear()
        self.mgr.on_proxy_disconnect(self.name)

    def on_helper_proxy(self, bind_addr, remote_addr):
        print "helper proxy:", bind_addr, remote_addr
        self.proxy_helper.close()
        self.proxy_helper = None
        self.local_proxy = LocalProxy(self, self.proxy_addr)
        self.remote_proxy = RemoteProxy(self, bind_addr, remote_addr)

    def on_remote_recv(self, data):
        self.local.on_recv_data(data)

    def on_local_recv(self, data):
        self.remote.on_recv_data(data)

    def clear(self):
        if self.proxy_helper is not None:
            self.proxy_helper.close()
        if self.remote_proxy is not None:
            self.remote_proxy.close()
        if self.local_proxy:
            self.local_proxy.close()

    def update(self):
        if self.proxy_helper:
            self.proxy_helper.update()
        if self.remote_proxy:
            self.remote_proxy.update()
        if self.local_proxy:
            self.local_proxy.update()

class ProxyServer(asyncore.dispatcher):

    def __init__(self, name, proxy_addr, remote_addr):
        asyncore.dispatcher.__init__(self)
        self.name = name
        self.proxy_addr = proxy_addr
        self.remote_addr = remote_addr
        self.create_socket(socket.af_inet, socket.sock_stream)
        self.set_reuse_addr()
        self.connect(self.remote_addr)
        self.last_time = time.time()
        self.connect_count = 1
        self.status = "connecting"
        self.proxys = {}

    def handle_connect(self):
        print "connect nat success"
        self.status = "connected"
        self.last_time = time.time()
        self.connect_count = 0
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.send_buffer += (struct.pack("!2H", len(self.name), S2N_REGIST_SERV_ASK) + self.name)

    def handle_close(self):
        print "connector nat failed"
        self.close()
        self.status = "disconnect"

    def handle_error(self):
        print "connect nat error"
        self.handle_close()

    def reconnect(self):
        print "reconnect nat"
        self.status = "connecting"
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect(self.remote_addr)
        self.last_time = time.time()
        self.connect_count += 1
        if self.connect_count > 5:
            self.connect_count = 5

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

            if cmd == N2S_REQUEST_PROXY_ASK:
                self.create_new_proxy(body)

    def writable(self):
        return self.status == "connecting" or len(self.send_buffer) > 0

    def handle_write(self):
        if len(self.send_buffer) <= 0:
            return
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]
        self.last_time = time.time()

    def create_new_proxy(self, name):
        proxy = self.proxys.get(name)
        if proxy:
            proxy.clear()
        self.proxys[name] = ProxyManager(self, name, self.proxy_addr, self.remote_addr)

    def on_proxy_disconnect(self, name):
        del self.proxys[name]

    def update(self):
        now_time = time.time()
        if self.status == "disconnect":
            if now_time >= self.last_time + 2 ** self.connect_count:
                self.reconnect()
        elif self.status == "connected":
            if now_time >= self.last_time + 30:
                self.send_buffer += struct.pack("!2H", 0, HEART_BEAT)
                self.last_time = time.time()
        for name in self.proxys:
            self.proxys[name].update()

serv = ProxyServer(SERV_NAME, PROXY_ADDR, NAT_ADDR)

while True:
    asyncore.loop(timeout = 1, count = 2)
    serv.update()
