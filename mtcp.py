#!/usr/bin/env python
#code: utf-8

class MTcpBuffer:
    def __init__(self, data):
        pass
    def len(self):
        pass
    def append(self, data):
        pass

class MTcpStream:
    def __init__(self):
        self._snd_buf_list = []
        self._snd_buf_cur = 0
        self._snd_buf_len = 0
        self._snd_buf_max = 0
        self._mss = 100
    def send(self, data):
        left_len = min(len(data), self._snd_buf_max - self._snd_buf_len)
        if left_len <= 0:
            return 0
        snd_len = 0
        if self._snd_buf_cur < len(self._snd_buf_list):
            buf = self._snd_buf_list[-1]
            if buf.len() < self._mss:
                snd_len = self._mss - buf.len()
                if snd_len > left_len:
                    snd_len = left
                buf.append(data[:snd_len])
        while left_len > 0:
            if left_len < self._mss:
                self._snd_buf_list.append(MTcpBuffer(data[snd_len:]))
                break

    def recv(self, len):
        pass
    def input(self, data):
        pass
    def update(self):
        pass

if __name__ == "__main__":
    pass
