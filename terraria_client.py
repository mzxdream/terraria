#!/usr/bin/env python

import socket
import asyncore
import struct
import time

serv_name = "mzx"

local_addr = ("", 7777)
nat_addr = ("", 7777)

header_size = 4

HEART_BEAT = 0

S2N_REGIST_SERV_ASK = 1
N2S_REGIST_SERV_RET = 2

S2N_REGIST_PROXY_ASK = 3
N2S_REGIST_PROXY_RET = 4

N2S_CLIENT_CONNECT_ASK = 3
S2N_CLIENT_CONNECT_RET = 4

S2N_CONNECT_CLIENT_ASK = 5
N2S_CONNECT_CLIENT_RET = 6

class LocalProxy(asyncore.dispatcher):

    def __init__(self, mgr):
        asyncore.dispatcher.__init__(self)
        self.mgr = mgr
        self.addr = dest_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect(self.addr)
        self.last_time = time.time()
        self.connect_count = 1
        self.status = "connecting"
        self.send_buffer = bytes()

    def handle_connect(self):
        self.status = "connected"
        print "connect server success"
        self.mgr.on_local_connect()

    def handle_close(self):
        print "server close"
        self.close()
        if self.status == "connected":
            self.mgr.on_local_disconnect()
            return
        self.status = "disconnect"

    def handle_error(self):
        print "server error"
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
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect(self.addr)
        self.last_time = time.time()
        self.connect_count += 1
        self.status = "connecting"

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
        self.addr = remote_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(self.bind_addr)
        self.connect(self.addr)
        self.last_time = time.time()
        self.connect_count = 1
        self.status = "connecting"
        self.send_buffer = bytes()

    def handle_connect(self):
        self.status = "connected"
        print "connect server success"
        self.mgr.on_remote_connect()

    def handle_close(self):
        print "server close"
        self.close()
        if self.status == "connected":
            self.mgr.on_remote_disconnect()
            return
        self.status = "disconnect"

    def handle_error(self):
        print "server error"
        self.handle_close()

    def handle_read(self):
        data = self.recv(2048)
        if not data:
            return
        self.mgr.on_remote_recv(data)

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
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(self.bind_addr)
        self.connect(self.addr)
        self.last_time = time.time()
        self.connect_count += 1
        self.status = "connecting"

    def update(self):
        now_time = time.time()
        if self.status == "disconnect":
            if now_time >= self.last_time + 2 ** self.connet_count:
                self.reconnect()

class ProxyHelper(asyncore.dispatcher):

    def __init__(self, mgr, name, addr):
        asyncore.dispatcher.__init__(self)
        self.mgr = mgr
        self.name = name
        self.addr = addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect(self.addr)
        self.last_time = time.time()
        self.connect_count = 1
        self.status = "connecting"

    def handle_connect(self):
        self.status = "connected"
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.send_buffer += (struct.pack("!2H", len(self.name), S2N_REGIST_PROXY_ASK) + self.name)
        print "connect server success"
        self.mgr.on_helper_connect()

    def handle_close(self):
        print "server close"
        self.close()
        if self.status == "connected":
            self.mgr.on_helper_disconnect()
            return
        self.status = "disconnect"

    def handle_error(self):
        print "server error"
        self.handle_close()

    def handle_read(self):
        data = self.recv(2048)
        if not data:
            return
        self.recv_buffer += data
        self.decode_package()

    def writable(self):
        return self.status != "connected" or len(self.send_buffer) > 0

    def handle_write(self):
        if len(self.send_buffer) <= 0:
            return
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

    def decode_package(self):
        while True:
            if len(self.recv_buffer) < header_size:
                break
            body_size, cmd = struct.unpack("!2H", self.recv_buffer[:header_size])
            if len(self.recv_buffer) < header_size + body_size:
                break
            body = self.recv_buffer[header_size:header_size+body_size]
            self.recv_buffer = self.recv_buffer[header_size+body_size:]
            self.dispatch_package(cmd, body)

    def dispatch_package(self, cmd, body):
        if cmd == N2S_REGIST_PROXY_RET:
            addr = body.split(":")
            if len(addr) != 2:
                self.handle_close()
                return
            addr = (addr[0], int(addr[1]))
            local_addr = self.socket.getsockname()
            self.mgr.on_helper_regist(local_addr, addr)

    def reconnect(self):
        if self.connet_count > 10:
            self.handle_close()
            return
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect(self.addr)
        self.last_time = time.time()
        self.connect_count += 1
        self.status = "connecting"

    def update(self):
        now_time = time.time()
        if self.status == "disconnect":
            if now_time >= self.last_time + 2 ** self.connet_count:
                self.reconnect()

class ProxyManager():
    def __init__(self, mgr, name, addr):
        self.mgr = mgr
        self.name = name
        self.helper = ProxyHelper(self, name, addr)

    def on_helper_connect(self):
        print "helper:", self.name, "connect"

    def on_helper_disconnect(self):
        print "helper:", self.name, "disconnect"
        self.clear()
        self.mgr.on_proxy_disconnect(self.name)

    def on_remote_connect(self):
        print "remote:", self.name, "connect"

    def on_remote_disconnect(self):
        print "remote:", self.name, "disconnect"
        self.clear()
        self.mgr.on_proxy_disconnect(self.name)

    def on_local_connect(self):
        print "connect:", self.name, "connect"

    def on_local_disconnect(self):
        print "connect:", self.name, "disconnect"
        self.clear()
        self.mgr.on_proxy_disconnect(self.name)

    def on_helper_regist(self, bind_addr, remote_addr):
        print "proxy:", bind_addr, remote_addr
        self.helper.clear()
        self.local = LocalProxy(self)
        self.remote = RemoteProxy(self, bind_addr, remote_addr)

    def on_remote_recv(self, data):
        self.local.on_recv_data(data)

    def on_local_recv(self, data):
        self.remote.on_recv_data(data)

    def clear(self):
        if self.helper:
            self.helper.close()
        if self.remote:
            self.remote.close()
        if self.local:
            self.local.close()

    def update(self):
        if self.helper:
            self.helper.update()
        if self.remote:
            self.remote.update()
        if self.local:
            self.local.update()

class ProxyManager(asyncore.dispatcher):

    def __init__(self, serv_name, bind_addr, remote_addr):
        asyncore.dispatcher.__init__(self)
        self.serv_name = serv_name
        self.bind_addr = bind_addr
        self.remote_addr = remote_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(self.bind_addr)
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair

    def handle_connect(self):
        self.status = "connected"
        self.last_time = time.time()
        self.connect_count = 0
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.send_buffer += (struct.pack("!2H", len(self.name), S2N_REGIST_SERV_ASK) + self.name)
        print "connect server success"

    def handle_close(self):
        self.status = "disconnect"
        print "nat connector server close"
        self.close()


    def handle_error(self):
        self.handle_close()
        print "server error"

    def reconnect(self):
        print "reconnect"
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect(self.addr)
        self.last_time = time.time()
        self.connect_count += 1
        if self.connect_count > 5:
            self.connect_count = 5
        self.status = "connecting"

    def handle_read(self):
        data = self.recv(2048)
        if not data:
            return
        self.recv_buffer += data
        self.decode_package()

    def writable(self):
        return self.status == "connecting" or len(self.send_buffer) > 0

    def handle_write(self):
        if len(self.send_buffer) <= 0:
            return
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]
        self.last_time = time.time()

    def decode_package(self):
        while True:
            if len(self.recv_buffer) < header_size:
                break
            body_size, cmd = struct.unpack("!2H", self.recv_buffer[:header_size])
            if len(self.recv_buffer) < header_size + body_size:
                break
            body = self.recv_buffer[header_size:header_size+body_size]
            self.recv_buffer = self.recv_buffer[header_size+body_size:]
            self.dispatch_package(cmd, body)

    def dispatch_package(self, cmd, body):
        if cmd == N2S_CLIENT_CONNECT_ASK:
            self.create_new_proxy(body)

    def create_new_proxy(self, key):
        self.close_proxy(key)
        self.proxys[key] = ProxyManager(self, key, self.addr)

    def on_proxy_disconnect(self, key):
        del self.proxys[key]

    def update(self):
        now_time = time.time()
        if self.status == "disconnect":
            if now_time >= self.last_time + 2 ** self.connect_count:
                self.reconnect()
        elif self.status == "connected":
            if now_time >= self.last_time + 30:
                self.send_buffer += struct.pack("!2H", 0, HEART_BEAT)
                self.last_time = time.time()
        for key in self.proxys:
            self.proxys[key].update()

handler = NatConnector(serv_name, nat_addr)

while True:
    asyncore.loop(timeout = 1, count = 2)
    handler.update()
