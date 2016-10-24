#!/usr/bin/env python

import socket
import time
import asyncore

NAT_ADDR = ("", 7777)

class UdpServer(asyncore.dispatcher):

    def __init__(self, nat_addr):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.set_reuse_addr()
        self.nat_addr = nat_addr
        self.remote_addr = None
        self.connected_remote = False
        self.sendto("server", self.nat_addr)

    def handle_read(self):
        data, addr = self.recvfrom(2048)
        print "recvfrom: %s->%s" % (str(addr), data)
        if self.remote_addr is None:
            addr = data.split(":")
            self.remote_addr = (addr[0], int(addr[1]))
            return
        if data == "ping":
            self.sendto("pong", self.remote_addr)
            self.connected_remote = True
            return
        self.sendto("ret->" + data, self.remote_addr)

    def update(self):
        if self.remote_addr is None:
            return
        if not self.connected_remote:
            self.sendto("ping", self.remote_addr)
            print "sendto ping ->", self.remote_addr
            time.sleep(2)
            return

serv = UdpServer(NAT_ADDR)

while True:
    asyncore.loop(timeout = 1, count = 1)
    serv.update()
