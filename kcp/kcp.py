#!/usr/bin/env python
# coding: utf-8

from .kcp_internal import (
    const,
    u32_next,
    u32_diff
)

from .kcp_segment import (
    KcpSegment
)

from .kcp_header import (
    KcpHeader
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
        seq = self._snd_nxt
        while True:
            if len(self._snd_buf) <= 0:
                break
            segment = self._snd_buf[-1]
            if u32_diff(segment.get_seq(), self._snd_nxt) < 0:
                break
            seq = u32_next(segment.get_seq())
            copied_len = min(len(data), self._mss - segment.buf_len())
            if copied_len <= 0:
                copied_len = 0
                break
            segment.append_buf(data[:copied_len])
            break
        while copied_len < len(data) and u32_diff(seq, self._snd_una) <= self._snd_wnd:
            copy_len = min(len(data) - copied_len, self._mss)
            segment = KcpSegment()
            segment.set_seq(seq)
            segment.write_buf(data[copied_len: copied_len + copy_len])
            self._snd_buf.append(segment)
            copied_len += copy_len
            seq = u32_next(seq)
        return copied_len

    def update_ack(self, rtt):
        if rtt <= 0:
            return
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
        self._rto = min(max(self._rx_minrto, rto), const.KCP_RTO_MAX)

    def update_una(self):
        if len(self._snd_buf) <= 0:
            self._snd_una = self._snd_nxt
        else:
            self._snd_una = self._snd_buf[0].get_seq()

    def check_ack(self, seq):
        if u32_diff(seq, self._snd_una) < 0 or u32_diff(seq, self._snd_nxt) >= 0:
            return
        for index, segment in enumerate(self._snd_buf):
            diff = u32_diff(seq, segment.get_seq())
            if diff < 0:
                break
            elif diff == 0:
                self._snd_buf.pop(index)
                break
        self.update_una()

    def check_una(self, una):
        if u32_diff(una, self._snd_una) < 0 or u32_diff(una, self._snd_nxt) >= 0:
            return
        while len(self._snd_buf) > 0:
            segment = self._snd_buf[0]
            if u32_diff(una, segment.get_seq()) <= 0:
                break
            self._snd_buf.pop(0)
        self.update_una()

    def check_fastack(self, seq):
        if u32_diff(seq, self._snd_una) < 0 or u32_diff(seq, self._snd_nxt) >= 0:
            return
        for segment in self._snd_buf:
            if u32_diff(seq, segment.get_seq()) <= 0:
                break
            segment.add_fastack()

    def append_data(self, segment):
        seq = segment.get_seq()
        if u32_diff(seq, self._rcv_nxt) < 0 or u32_diff(seq, self._rcv_nxt) >= self._rcv_wnd:
            return
        for index, segment in enumerate(self._rcv_buf):
            diff = u32_diff(seq, segment.get_seq())
            if diff > 0:
                continue
            if diff != 0:
                self._rcv_buf.insert(index, segment)
            break
        for segment in self._rcv_buf:
            diff = u32_diff(self._rcv_nxt, segment.get_seq())
            if diff != 0:
                break
            self._rcv_nxt = u32_next(self._rcv_nxt)

    def input(self, data):
        maxack = None
        una = self._snd_una
        while True:
            header, size = KcpHeader.parse_from(data)
            if header == None:
                break
            data = data[size:]
            self._rmt_wnd = header.get_wnd()
            self.check_una(header.get_una())
            if header.get_cmd() == const.KCP_CMD_ASK:
                self.update_ack(u32_diff(self._current, header.get_ts()))
                self.check_ack(header.get_seq())
                if maxack == None or u32_diff(maxack, header.get_seq()) < 0:
                    maxack = header.get_seq()
            elif header.get_cmd() == const.KCP_CMD_PUSH:
                if u32_diff(header.get_seq(), self._rcv_nxt) >= 0 and u32_diff(header.get_seq(), self.rcv_nxt) < self._rcv_wnd:
                    segment = KcpSegment()
                    segment.set_seq(header.get_seq())
                    segment.write_buf(data[:header.get_len()])
                    data = data[header.get_len():]
                    self.append_data(segment)
            elif header.get_cmd() == const.KCP_CMD_WASK:
                self._probe |= const.KCP_ASK_TELL

        if maxack != None:
            self.update_fastack(maxack)

        if u32_diff(self._snd_una, una) > 0 and self._cwnd < self._rmt_wnd:
            if self._cwnd < self._ssthresh:
                self._cwnd += 1
                self._incr += self._mss
            else:
                self._incr = max(self._incr, self._mss)
                self._incr += (self._mss * self._mss / self._incr + self._mss / 16)
                if (self._cwnd + 1) * self._mss <= self._incr:
                    self._cwnd += 1
            if self._cwnd > self._rmt_wnd:
                self._cwnd = self._rmt_wnd
                self._incr = self._rmt_wnd * self._mss

    def flush(self):
        data = bytes()
        header = KcpHeader()
        header.set_seq(0)
        header.set_una(self._rcv_nxt)
        header.set_cmd(const.KCP_CMD_ACK)
        header.set_wnd(self._rcv_wnd - u32_diff(self._rcv_nxt - 123))
        header.set_len(0)
        header.set_ts(0)
        while len(self._acklist) > 0:
            ack = self._acklist.pop(0)
            header.set_seq(ack[0])
            header.set_ts(ack[1])
            info = header.stringify()
            if len(data) + len(info) > self._mtu:
                self._output(data)
                data = bytes()
            data += info

        if self._rmt_wnd <= 0:
            if self._probe_wait == 0:
                self._probe_wait = const.KCP_PROBE_INIT
                self._ts_probe = self._current + self._probe_wait
            else:
                if u32_diff(self._current, self._ts_probe) >= 0:
                    self._probe_wait = max(self._probe_wait, const.KCP_PROBE_INIT)
                    self._probe_wait += self._probe_wait / 2
                    self._probe_wait = min(self._probe_wait, const.KCP_PROBE_LIMIT)
                    self._ts_probe = self._current + self._probe_wait
                    self._probe |= const.KCP_ASK_SEND
        else:
            self._ts_probe = 0
            self._probe_wait = 0

        if self._probe & const.KCP_ASK_SEND:
            header.set_cmd(const.KCP_CMD_WASK)
            info = header.stringify()
            if len(data) + len(info) > self._mtu:
                self.output(data)
                data = bytes()
            data += info

        if self._probe & const.KCP_ASK_TELL:
            info = header.stringify()
            header.set_cmd(const.KCP_CMD_WINS)
            if len(data) + len(info) > self._mtu:
                self._output(data)
                data = bytes()
            data += info

        self._probe = 0

        cwnd = min(self._snd_wnd, self._rmt_wnd)
        if self._nocwnd == 0:
            cwnd = min(self._cwnd, cwnd)

        for segment in self._snd_buf:
            if u32_diff(segment.get_seq(), self._rcv_nxt) >= cwnd:
                break
            if segment.get_xmit() == 0:
                segment.set_rto(self._rto)
                segment.set_resentts =
