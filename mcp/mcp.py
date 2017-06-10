#!/usr/bin/env python
# coding: utf-8

def u32_next(a):
    return (a + 1) & 0xFFFFFFFF

def u32_before(a, b):
    result = a - b
    if result < 0:
        return result >= -0x7FFFFFFF
    return result > 0x7FFFFFFF

def u32_before_eq(a, b):
    result = a - b
    if result <= 0:
        return result >= -0x7FFFFFFF
    return result > 0x7FFFFFFF

def u32_after(a, b):
    result = a - b
    if result <= 0:
        return result < -0x7FFFFFFF
    return result <= 0x7FFFFFFF

def u32_after_eq(a, b):
    result = a - b
    if result < 0:
        return result < -0x7FFFFFFF
    else:
        return result <= 0x7FFFFFFF


class McpSegment:
    def __init__(self):
        self._seq = 0
        self._ack = 0
        self._una = 0
        self._cmd = 0
        self._wnd = 0
        self._len = 0

    @staticmethod
    def parseFromData(data):
        pass

class McpHandler:
    def __init__(self):
        self._rcv_nxt = 0
        self._snd_nxt = 0
        self._snd_una = 0

        self._snd_wnd = 0
        self._rcv_wnd = 0
        self._rmt_wnd = 0

        self._cwnd = 0

        self._snd_buf = []
        self._snd_cache = []
        self._rcv_buf = []
        self._snd_cache = []

        self._snd_cb = None
        self._rcv_cb = None

        self._cur_ts = 0

        self._mtu = 1440
        self._mss = 1330

    def get_send_cache_avail(self):
        if len(self._snd_cache) > 0:
            seg = self._snd_cache[-1]
            avail_len = self._mss - seg.get_data_len()
            if avail_len <= 0:
                return (self._snd_wnd - len(self._snd_cache)) * self._mss + avail_len
            return (self._snd_wnd - len(self._snd_cache)) * self._mss + avail_len
        return self._snd_wnd * self._mss

    def send(self, data):
        if len(data) <= 0:
            return 0
        if len(data) > self.get_send_cache_avail():
            return -1
        index = 0
        if len(self._snd_cache) > 0:
            seg = self._snd_cache[-1]
            avail_len = self._mss - seg.get_data_len()
            if avail_len > 0:
                seg.append_data(data[:avail_len])
                index += avail_len
        while index <= len(data):
            seg = McpSegment(data[index: index + self._mss])
            self._snd_cache.append(seg)
            index += self._mss
        return 0

    def recv(self, data, ts):
        if len(data) <= 0:
            return
        while True:
            ret = McpSegment.parseFromData(data)


    def update(self):
        pass

    def next_update_ts(self, cur_ts):
        pass

if __name__ == "__main__":
    pass
