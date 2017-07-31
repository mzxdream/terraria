#!/usr/bin/env python
# coding: utf-8

class KcpSegment:

    def __init__(self):
        self._seq = 0
        self._buf = bytes()
        self._fastack = 0
        self._resendcnt = 0
        self._resendts = 0

    def set_seq(self, seq):
        self._seq = seq

    def get_seq(self):
        return self._seq

    def write_buf(self, buf):
        self._buf = buf

    def append_buf(self, buf):
        self._buf += buf

    def read_buf(self, size):
        if size <= 0:
            return bytes()
        buf = self._buf[:size]
        self._buf = self._buf[size:]
        return buf

    def buf_len(self):
        return len(self._buf)

    def get_buf(self):
        return self._buf

    def add_fastack(self, count = 1):
        self._fastack += count

    def get_fastack(self):
        return self._fastack

    def add_resendcnt(self, count = 1):
        self._resendcnt += count

    def get_resendcnt(self):
        return self._resendcnt

    def set_resendts(self, ts):
        self._resendts = ts

    def get_resendts(self):
        return self._resendts
