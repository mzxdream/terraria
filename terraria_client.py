#!/usr/bin/env python

import socket
import asyncore
import struct
import time

serv_name = "mzx"

proxy_addr = ("", 7777)
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

C2N_REQUEST_PROXY_ASK = 10
N2C_REQUEST_PROXY_RET = 11

class LocalProxy(asyncore.dispatcher):

    def __init__(self, mgr, sock):
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
        asyncore.dispatcher.__init__(self)
        self.mgr = mgr
        self.bind_addr = bind_addr
        self.remote_addr = remote_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.listen(5)
        self.last_time = time.time()
        self.send_buffer = bytes()

    def readable(self):
        return self.remote_connector is None

    def handle_accept(self):
        if self.remote_connector is not None:
            return
        pair = self.accept()
        if pair is None:
            return
        sock, addr = pair
        if addr[0] != self.remote_addr[0] or addr[1] != self.remote_addr[1]:
            return
        self.remote_connector = RemoteConnector(self)
        self.remote_connector.on_recv_data(self.send_buffer)

    def on_connector_disconnect(self):
        self.close()
        self.mgr.on_remote_disconnect()

    def on_connector_recv(self, data):
        self.mgr.on_remote_recv(data)

    def on_recv_data(self, data):
        if self.remote_connector is None:
            self.send_buffer += data
            return
        self.remote_connector.on_recv_data(data)

    def update(self):
        if self.remote_connector:
            self.remote_connector.update()

class ProxyHelper(asyncore.dispatcher):

    def __init__(self, mgr, serv_name, remote_addr):
        asyncore.dispatcher.__init__(self)
        self.mgr = mgr
        self.serv_name = serv_name
        self.remote_addr = remote_addr
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.connect(self.remote_addr)
        self.last_time = time.time()
        self.connect_count = 1

    def handle_connect(self):
        self.send_buffer = bytes()
        self.recv_buffer = bytes()
        self.send_buffer += (struct.pack("!2H", len(self.serv_name), C2N_REQUEST_PROXY_ASK) + self.serv_name)

    def handle_close(self):
        if self.connected:
            self.close()
            self.mgr.on_helper_disconnect()
            return
        self.connected = False
        self.del_channel()

    def handle_error(self):
        self.handle_close()

    def handle_read(self):
        data = self.recv(2048)
        if not data:
            return
        self.recv_buffer += data
        while True:
            if len(self.recv_buffer) < header_size:
                break
            body_size, cmd = struct.unpack("!2H", self.recv_buffer[:header_size])
            if len(self.recv_buffer) < header_size + body_size:
                break
            body = self.recv_buffer[header_size:header_size+body_size]
            self.recv_buffer = self.recv_buffer[header_size+body_size:]

            if cmd == N2C_REQUEST_PROXY_RET:
                addr = body.split(":")
                if len(addr) != 2:
                    self.handle_close()
                    print "helper proxy recv:", body
                    return
                bind_addr = self.socket.getsockname()
                remote_addr = (addr[0], int(addr[1]))
                self.connect(remote_addr)
                self.close()
                self.mgr.on_helper_proxy(bind_addr, remote_addr)
                return

    def writable(self):
        return not self.connected or len(self.send_buffer) > 0

    def handle_write(self):
        if len(self.send_buffer) <= 0:
            return
        sent = self.send(self.send_buffer)
        self.send_buffer = self.send_buffer[sent:]

    def reconnect(self):
        if self.connet_count > 10:
            self.handle_close()
            return
        self.connect_failed = False
        self.add_channel()
        self.connect(self.remote_addr)
        self.last_time = time.time()
        self.connect_count += 1

    def update(self):
        now_time = time.time()
        if self.connect_failed:
            if now_time >= self.last_time + 2 ** self.connet_count:
                self.reconnect()

class ProxyManager(asyncore.dispatcher):
    def __init__(self, mgr, sock, serv_name, remote_addr):
        self.mgr = mgr
        self.name = sock.fileno()
        self.local_proxy = LocalProxy(self, sock)
        self.proxy_helper = ProxyHelper(self, serv_name, remote_addr)
        self.recv_buffer = bytes()

    def on_local_disconnect(self):
        print self.name, " local proxy disconnect"
        self.clear()
        self.mgr.on_proxy_disconnect(self.name)

    def on_helper_disconnect(self):
        print self.name, " proxy helper disconnect"
        self.clear()
        self.mgr.on_proxy_disconnect(self.name)

    def on_remote_disconnect(self):
        print self.name, " remote proxy disconnect"
        self.clear()
        self.mgr.on_proxy_disconnect(self.name)

    def on_helper_proxy(self, bind_addr, remote_addr):
        print self.name, " helper proxy :", remote_addr
        self.proxy_helper.close()
        self.remote_proxy = RemoteProxy(self, bind_addr, remote_addr)
        self.remote_proxy.on_recv_data(self.recv_buffer)

    def on_local_recv(self, data):
        if not self.remote_proxy:
            self.recv_buffer += data
            return
        self.remote_proxy.on_recv_data(data)

    def on_remote_recv(self, data):
        self.local_proxy.on_recv_data(data)

    def clear(self):
        if self.proxy_helper:
            self.proxy_helper.close()
        if self.local_proxy:
            self.local_proxy.close()
        if self.remote_proxy:
            self.remote_proxy.close()

    def update(self):
        if self.proxy_helper:
            self.proxy_helper.close()
        if self.local_proxy:
            self.local_proxy.update()
        if self.remote_proxy:
            self.remote_proxy.update()

class Server(asyncore.dispatcher):

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
            self.create_new_proxy(sock, self.remote_addr)

    def handle_error(self):
        print "server error"

    def create_new_proxy(self, sock, remote_addr):
        self.close_proxy(sock.fileno())
        self.proxys[sock.fileno()] = ProxyManager(self, sock, self.serv_name, remote_addr)

    def on_proxy_disconnect(self, key):
        del self.proxys[key]

    def update(self):
        for key in self.proxys:
            self.proxys[key].update()

handler = Server(serv_name, proxy_addr, nat_addr)

while True:
    asyncore.loop(timeout = 1, count = 2)
    handler.update()
