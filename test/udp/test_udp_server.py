#!/usr/bin/env python

import socket
import sys

if len(sys.argv) < 2:
    print "input nat ip"
    sys.exit()

NAT_ADDR = (sys.argv[1], 7777)

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
