#!/usr/bin/env python

import socket
import asyncore
import time
import sys

if len(sys.argv) < 2:
    print "input nat ip"
    sys.exit()

NAT_ADDR = (sys.argv[1], 7777)

class UdpClient(asyncore.dispatcher):

    def __init__(self, nat_addr):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.set_reuse_addr()
        self.nat_addr = nat_addr
        self.remote_addr = None
        self.connected_remote = False
        self.sendto("client", self.nat_addr)

    def handle_close(self):
        print "closed"

    def handle_error(self):
        print "error"

    def handle_read(self):
        data, addr = self.recvfrom(2048)
        print "recvfrom: %s->%s" % (str(addr), data)
        if self.remote_addr is None:
            addr = data.split(":")
            self.remote_addr = (addr[0], int(addr[1]))
            return
        if data == "ping":
            return
        if data == "pong":
            self.connected_remote = True

    def update(self):
        if self.remote_addr is None:
            return
        if not self.connected_remote:
            time.sleep(1)
            self.sendto("ping", self.remote_addr)
            print "sendto ping ->", self.remote_addr
            return
        data = raw_input("input:")
        self.sendto(data, self.remote_addr)


serv = UdpClient(NAT_ADDR)

while True:
    asyncore.loop(timeout = 1, count = 1)
    serv.update()
