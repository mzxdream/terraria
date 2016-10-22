#!/usr/bin/env python

import socket
import asyncore
import struct
import time

SERV_NAME = "mzx"

BIND_ADDR = ("", 7777)
NAT_ADDR = ("", 7777)

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


class LocalProxy(asyncore.dispatcher):

    def __init__(self, mgr, sock):
        print "local proxy:", sock.fileno()
        asyncore.dispatcher.__init__(self, sock)
        self.mgr = mgr
        self.send_buffer = bytes()
        self.last_time = time.time()

    def handle_close(self):
        print "local proxy closed"
        self.close()
        self.mgr.on_local_disconnect()

    def handle_error(self):
        print "local proxy error"
        self.handle_close()

    def handle_read(self):
        data = self.recv(2048)
        if not data:
            return
        self.last_time = time.time()
        self.mgr.on_local_recv(data)

    def on_recv_data(self, data):
        self.send_buffer += data

    def writable(self):
        return len(self.send_buffer) > 0

    def handle_write(self):
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

    def update(self):
        now_time = time.time()
        if now_time >= self.last_time + 180:
            print "local proxy timeout"
            self.handle_close()

class RemoteConnector(asyncore.dispatcher):
    def __init__(self, mgr, sock):
        print "remote connector:", sock.fileno()
        asyncore.dispatcher.__init__(self, sock)
        self.mgr = mgr
        self.send_buffer = bytes()
        self.last_time = time.time()

    def handle_close(self):
        print "remote connector closed"
        self.close()
        self.mgr.on_connector_disconnect()

    def handle_error(self):
        print "remote connector error"
        self.handle_close()

    def handle_read(self):
        data = self.recv(2048)
        if not data:
            return
        self.last_time = time.time()
        self.mgr.on_connector_recv(data)

    def on_recv_data(self, data):
        self.send_buffer += data

    def writable(self):
        return len(self.send_buffer) > 0

    def handle_write(self):
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

    def update(self):
        now_time = time.time()
        if now_time >= self.last_time + 180:
            print "remote connector timeout"
            self.handle_close()

class RemoteProxy(asyncore.dispatcher):

    def __init__(self, mgr, bind_addr, remote_addr):
        print "remote proxy:", bind_addr, remote_addr
        asyncore.dispatcher.__init__(self)
        self.mgr = mgr
        self.bind_addr = bind_addr
        self.remote_addr = remote_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.last_time = time.time()
        self.recv_buffer = bytes()
        self.remote_connector = None
        self.listen(5)

    def readable(self):
        return self.remote_connector is None

    def handle_accept(self):
        if self.remote_connector is not None:
            return
        pair = self.accept()
        if pair is None:
            return
        sock, addr = pair
        print "remote proxy accept:", addr
        if addr[0] != self.remote_addr[0] or addr[1] != self.remote_addr[1]:
            return
        self.remote_connector = RemoteConnector(self)
        self.remote_connector.on_recv_data(self.recv_buffer)
        self.recv_buffer = bytes()

    def on_connector_disconnect(self):
        print "remote proxy diconnect"
        self.close()
        self.mgr.on_remote_disconnect()

    def on_connector_recv(self, data):
        self.mgr.on_remote_recv(data)

    def on_recv_data(self, data):
        if self.remote_connector is None:
            self.recv_buffer += data
            return
        self.remote_connector.on_recv_data(data)

    def update(self):
        if self.remote_connector is not None:
            self.remote_connector.update()

class ProxyHelper(asyncore.dispatcher):

    def __init__(self, mgr, serv_name, remote_addr):
        print "proxy helper:", serv_name, remote_addr
        asyncore.dispatcher.__init__(self)
        self.mgr = mgr
        self.serv_name = serv_name
        self.remote_addr = remote_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.last_time = time.time()
        self.connect_count = 1
        self.status = "connecting"
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.connect(self.remote_addr)

    def handle_connect(self):
        print "proxy helper connect"
        self.status = "connected"
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.send_buffer += (struct.pack("!2H", len(self.serv_name), C2N_REQUEST_PROXY_ASK) + self.serv_name)

    def handle_close(self):
        print "proxy helper closed"
        self.close()
        if self.status == "connected":
            self.mgr.on_helper_disconnect()
            return
        self.status = "disconnect"

    def handle_error(self):
        print "proxy helper error"
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

            print "proxy helper recv:", cmd, body
            if cmd == N2C_REQUEST_PROXY_RET:
                addr = body.split(":")
                if len(addr) != 2:
                    self.handle_close()
                    print "helper proxy recv:", body
                    return
                bind_addr = self.socket.getsockname()
                remote_addr = (addr[0], int(addr[1]))
                self.close()
                self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
                self.set_reuse_addr()
                self.bind(bind_addr)
                self.connect(remote_addr)
                self.close()
                self.mgr.on_helper_proxy(bind_addr, remote_addr)

    def writable(self):
        return self.status == "connecting" or len(self.send_buffer) > 0

    def handle_write(self):
        if len(self.send_buffer) <= 0:
            return
        print "proxy helper send:", self.send_buffer
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

    def reconnect(self):
        print "proxy helper reconnect"
        if self.connect_count > 10:
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
            if now_time >= self.last_time + 2 ** self.connect_count:
                self.reconnect()

class ProxyManager(asyncore.dispatcher):
    def __init__(self, mgr, name, sock, serv_name, remote_addr):
        print "proxy manager:", name, serv_name, remote_addr
        self.mgr = mgr
        self.name = name
        self.local_proxy = LocalProxy(self, sock)
        self.remote_proxy = None
        self.proxy_helper = ProxyHelper(self, serv_name, remote_addr)
        self.recv_buffer = bytes()

    def on_local_disconnect(self):
        print self.name, " local proxy disconnect"
        self.clear()
        self.mgr.on_proxy_disconnect(self.name)

    def on_helper_disconnect(self):
        print self.name, " proxy helper disconnect"
        if self.proxy_helper is None:
            return
        self.clear()
        self.mgr.on_proxy_disconnect(self.name)

    def on_remote_disconnect(self):
        print self.name, " remote proxy disconnect"
        self.clear()
        self.mgr.on_proxy_disconnect(self.name)

    def on_helper_proxy(self, bind_addr, remote_addr):
        print self.name, " helper proxy :", remote_addr
        self.proxy_helper.close()
        self.proxy_helper = None
        self.remote_proxy = RemoteProxy(self, bind_addr, remote_addr)
        self.remote_proxy.on_recv_data(self.recv_buffer)
        self.recv_buffer = bytes()

    def on_local_recv(self, data):
        if self.remote_proxy is None:
            self.recv_buffer += data
            return
        self.remote_proxy.on_recv_data(data)

    def on_remote_recv(self, data):
        self.local_proxy.on_recv_data(data)

    def clear(self):
        if self.proxy_helper is not None:
            self.proxy_helper.close()
        if self.local_proxy is not None:
            self.local_proxy.close()
        if self.remote_proxy is not None:
            self.remote_proxy.close()

    def update(self):
        if self.proxy_helper is not None:
            self.proxy_helper.update()
        if self.local_proxy is not None:
            self.local_proxy.update()
        if self.remote_proxy is not None:
            self.remote_proxy.update()

class ProxyServer(asyncore.dispatcher):

    def __init__(self, serv_name, bind_addr, remote_addr):
        asyncore.dispatcher.__init__(self)
        self.serv_name = serv_name
        self.bind_addr = bind_addr
        self.remote_addr = remote_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(self.bind_addr)
        self.proxys = {}
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            self.create_new_proxy(sock, self.remote_addr)

    def handle_error(self):
        print "proxy server error"

    def create_new_proxy(self, sock, remote_addr):
        print "create new proxy:", remote_addr
        name = sock.fileno()
        proxy = self.proxys.get(name)
        if proxy is not None:
            proxy.clear()
        self.proxys[name] = ProxyManager(self, name, sock, self.serv_name, remote_addr)

    def on_proxy_disconnect(self, name):
        del self.proxys[name]

    def update(self):
        for name in self.proxys.keys():
            self.proxys[name].update()

serv = ProxyServer(SERV_NAME, BIND_ADDR, NAT_ADDR)

while True:
    asyncore.loop(timeout = 1, count = 2)
    serv.update()
