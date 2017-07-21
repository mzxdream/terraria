#!/usr/bin/env python
# coding: utf-8

from .kcp_internal import (
    const,
    u32_next,
    u32_diff
)

class Kcp(object):
    def __init__(self):
        self._snd_una = 0
        self._snd_nxt = 0
        self._rcv_nxt = 0
        self._copied_nxt = 0

        self._ts_recent = 0
        self._ts_lastack = 0
        self._ts_probe = 0
        self._probe_wait = 0

        self._snd_wnd = const.KCP_WND_SND
        self._rcv_wnd = const.KCP_WND_RCV
        self._rmt_wnd = const.KCP_WND_RCV

        self._cwnd = 0
        self._incr = 0
        self._probe = 0

        self._mtu = const.KCP_MTU_DEF
        self._mss = self._mtu - const.KCP_OVERHEAD

        self._snd_buf = []
        self._rcv_buf = []
        self._state = 0

        self._acklist = []

        self._rx_srtt = 0
        self._rx_rttval = 0
        self._rx_rto = const.KCP_RTO_DEF
        self._rx_minrto = const.KCP_RTO_MIN

        self._current = 0
        self._interval = const.KCP_INTERVAL
        self._ts_flush = const.KCP_INTERVAL
        self._nodelay = 0
        self._updated = 0
        self._ssthresh = const.KCP_THRESH_INIT
        self._fastresend = 0
        self._nocwnd = 0
        self._xmit = 0
        self._dead_link = const.KCP_DEADLINK

        self._output_cb = None
        self._recv_cb = None

    def set_output_cb(self, output_cb):
        self._output_cb = output_cb

    def set_recv_cb(self, recv_cb):
        self._recv_cb = recv_cb

    def recv(self, size):
        data = bytes()
        if size <= 0:
            raise ValueError("size:%s is less than 1" % (size))

        while len(data) < size and len(self._rcv_buf) > 0:
            segment = self._rcv_buf[0]
            if segment.get_seq() != self._copied_nxt:
                break
            data += segment.read_buf(size - len(data))
            if segment.buf_len() <= 0:
                self._rcv_buf.pop(0)
                self._copied_nxt = u32_next(self._copied_nxt)
        return data

    def send(self, data):
        if len(data) <= 0:
            return 0
        copied_len = 0
        while True:
            if len(self._snd_buf) <= 0:
                break
            segment = self._snd_buf[-1]
            if u32_diff(segment.get_seq(), self._snd_nxt) < 0:
                break
            copied_len = min(len(data), self._mss - segment.buf_len())
            if copied_len <= 0:
                copied_len = 0
                break
            segment.append_buf(data[:copied_len])
            break
        while copied_len < len(data) and u32_diff()
        return 0

    def update_ack(self, rtt):
        rto = 0
        if self._rx_srtt == 0:
            self._rx_srtt = rtt
            self._rx_rttval = rtt // 2
        else:
            delta = rtt - self._rx_srtt
            if delta < 0:
                delta = -delta
            self._rx_rttval = (3 * self._rx_rttval + delta) // 4
            self._rx_srtt = (7 * self._rx_srtt + rtt) // 8
            if self._rx_srtt < 1:
                self._rx_srtt = 1
        rto = self._rx_srtt + max(self._interval, 4 * self._rx_rttval)
        self._rto = min(max(self._rx_minrto, rto), KCP_RTO_MAX)

    def shrink_buf(self):
        if len(self._snd_buf) <= 0:
            self._snd_una = self._snd_nxt
        else:
            self._snd_una = self._snd_buf[-1].get_sn()

    def parse_ack(self, sn):
        if u32_diff(sn, self._snd_una) < 0 or u32_diff(sn, self._snd_nxt) >= 0:
            return
        for start in range(self._snd_buf):
            segment = self._snd_buf[start]
            if u32_diff(sn, segment.get_sn()) < 0:
                break
            if sn == segment.get_sn():
                self._snd_buf.pop(start)
                break

    def parse_una(self, una):
        start - 0
        for start in range(self._snd_buf):
            segment = self._snd_buf[start]
            if u32_diff(una, segment.get_sn()) < 0:
                break

    def parse_fastack(self, sn):
        if u32_diff(sn, self._snd_una) < 0 or u32_diff(sn, self._snd_nxt):
            return
        for segment in self._snd_buf:
            if u32_diff(sn, segment.get_sn()) <= 0:
                break
            segment.add_fastack()

    def ack_push(self, sn, ts):
        self._acklist.push((sn, ts))

    def ack_get(self, index):
        return self._acklist[index]

    def parse_data(self, segment):
        sn = segment.get_sn()
        repeat = 0

        if u32_diff(sn, self._rcv_nxt) >= self._rcv_wnd or u32_diff(sn, self._rcv_nxt) < 0:
            return

        for i in range(self._rcv_buf):
            segment = self._rcv_buf[i]
            if segment.get_sn() == sn:
                break
            if u32_diff(sn, segment.get_sn()) > 0:
                self._rcv_buf.insert(i, segment)
                break

        while len(self._rcv_buf) > 0:
            segment = self._rcv_buf[0]
            if segment.get_sn() != self._rcv_nxt:
                break
            if len(self._rcv_queue) >= self._rcv_wnd:
                break
            self._rcv_queue.push(segment)
            self._rcv_buf.pop(0)

    def input(self, data):
        pass
