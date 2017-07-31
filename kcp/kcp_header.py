#!/usr/bin/env python
# coding: utf-8

import struct

class KcpHeader(object):

    def __init__(self):
        self._seq = 0
        self._ackseq = 0
        self._ts = 0
        self._ackts = 0
        self._cmd = 0
        self._wnd = 0
        self._size = 0

    def set_seq(self, seq):
        self._seq = seq

    def get_seq(self):
        return self._seq

    def set_ackseq(self, ackseq):
        self._ackseq = ackseq

    def get_ackseq(self):
        return self._ackseq

    def set_ts(self, ts):
        self._ts = ts

    def get_ts(self):
        return self._ts

    def set_ackts(self, ackts):
        self._ackts = ackts

    def get_ackts(self):
        return self._ackts

    def set_cmd(self, cmd):
        self._cmd = cmd

    def get_cmd(self):
        return self._cmd

    def set_wnd(self, wnd):
        self._wnd = wnd

    def get_wnd(self):
        return self._wnd

    def set_size(self, size):
        self._size = size

    def get_size(self):
        return self._size

    def stringify(self):
        return struct.pack("!IIIIIII", self._seq, self._ackseq, self._ts, self._ackts, self._cmd, self._wnd, self._size)

    @staticmethod
    def parse(data):
        if len(data) < 4 * 7:
            return None
        header = KcpHeader()
        header._seq, header._ackseq, header._ts, header._ackts, header._cmd, header._wnd, header._size = struct.unpack("!IIIIIII", data)
        return header
