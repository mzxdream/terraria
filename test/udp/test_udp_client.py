#!/usr/bin/env python

import socket
import time
import sys

if len(sys.argv) < 2:
    print "input nat ip"
    sys.exit()

NAT_ADDR = (sys.argv[1], 7777)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto("client", NAT_ADDR)

data, addr = sock.recvfrom(1024)
print "recvfrom: %s->%s" % (str(addr), data)

addr = data.split(":")

remote_addr = (addr[0], int(addr[1]))

while True:
    print "sendto: %s->123123" % (str(remote_addr))
    sock.sendto("123123", remote_addr)
    time.sleep(3)
