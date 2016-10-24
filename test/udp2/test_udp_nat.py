#!/usr/bin/env python

import socket

BIND_ADDR = ("", 7777)

client = None
server = None
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(BIND_ADDR)

while True:
    data, addr = sock.recvfrom(1024)
    print "recvform: %s->%s" % (str(addr), data)
    if data == "server":
        server = addr
    elif data == "client":
        client = addr
    if client is not None and server is not None:
        data = client[0] + ":" + str(client[1])
        sock.sendto(data, server)
        data = server[0] + ":" + str(server[1])
        sock.sendto(data, client)
        client = None
        server = None
