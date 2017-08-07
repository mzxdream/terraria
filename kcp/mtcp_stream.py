#!/usr/bin/env python
# coding: utf-8

import MTcpHeader

class MTcpStream:

    def __init__(self):
        self._write_seq = 0
        self._snd_una = self._write_seq
        self._snd_nxt = self._snd_una
        self._snd_wl1 = self._snd_una
        self._snd_wnd = 65535
        self._lsndtime = 0

        self._rcv_tsecr = 0
        self._rcv_tsval = 0
        self._rcv_nxt = 0
        self._copied_seq = self._rcv_nxt
        self._rcv_wup = self._rcv_nxt
        self._rcv_wnd = 88
        self._rcv_ssthresh = self._rcv_wnd

        self._fack = True
        self._state = 0
        self._ts_recent = self._rcv_tsval
        self._mstamp = 0

    def output(self):
        pass

    def input(self, buf):
        while True:
            header = MTcpHeader.parse(buf)
            if header == None:
                break
            if len(buf) < header.get_len():
                break
            data = buf[header.get_header_len():header.get_len()]
            buf = buf[header.get_len():]

            seq = header.get_seq()
            if u32_diff(seq, self._rcv_wup) >= 0 and u32_diff(seq, self._rcv_wup) <= self._rcv_wnd:
                break
            ack_seq = header.get_ack_seq()
            if u32_diff(ack_seq, self._snd_una) < 0:
                break








if __name__ == "__main__":
    pass
