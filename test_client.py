#!/usr/bin/env python

import socket

REMOTE_ADDR = ("", 7777)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(REMOTE_ADDR)
while True:
    cmd = raw_input("input cmd:")
    sock.sendall(cmd)
    data = sock.recv(1024)
    print "recv ->", data
sock.close()
