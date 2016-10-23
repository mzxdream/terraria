#!/usr/bin/env python

import socket
import time

NAT_ADDR = ("", 7777)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto("client", NAT_ADDR)

data, addr = sock.recvfrom(1024)
print "recvfrom: %s->%s" % (str(addr), data)

addr = data.split(":")

remote_addr = (addr[0], int(addr[1]))

while True:
    sock.sendto("1123123", remote_addr)
    time.sleep(3)
