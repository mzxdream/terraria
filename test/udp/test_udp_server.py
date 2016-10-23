#!/usr/bin/env python

import socket

NAT_ADDR = ("", 7777)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto("server", NAT_ADDR)

data, addr = sock.recvfrom(1024)
print "recvfrom: %s->%s" % (str(addr), data)

addr = data.split(":")

remote_addr = (addr[0], int(addr[1]))
sock.sendto("test hole", remote_addr)
sock.sendto("test hole", remote_addr)
sock.sendto("test hole", remote_addr)

while True:
    data, addr = sock.recvfrom(1024)
    print "recvfrom: %s->%s" % (str(addr), data)
