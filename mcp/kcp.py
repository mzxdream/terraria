#!/usr/bin/env python
# coding: utf-8

KCP_RTO_NDL = 30
KCP_RTO_MIN = 100
KCP_RTO_DEF = 200
KCP_RTO_MAX = 60000

KCP_CMD_PUSH = 81
KCP_CMD_ACK = 82
KCP_CMD_WASK = 83
KCP_CMD_WINS = 84

KCP_ASK_SEND = 1
KCP_ASK_TELL = 2

KCP_WND_SND = 32
KCP_WND_RCV = 32

KCP_MTU_DEF = 1400

KCP_ACK_FASK = 3

KCP_INTERVAL = 100

KCP_OVERHEAD = 24

KCP_DEADLINK = 20

KCP_THRESH_INIT = 2
KCP_THRESH_MIN = 2

KCP_PROBE_INIT = 7000
KCP_PROBE_LIMIT = 120000

def u32_next(a):
    return (a + 1) & 0xFFFFFFFF

def u32_diff(a, b):
    diff = a - b
    if diff > 0x7FFFFFFF:
        return diff - 0xFFFFFFFF
    if diff < -0x7FFFFFFF:
        return diff + 0xFFFFFFFF
    return diff

class KcpSegment:
    def __init__(self):
        self._cmd = 0
        self._wnd = 0
        self._ts = 0
        self._sn = 0
        self._una = 0
        self._resendts = 0
        self._rto = 0
        self._fastack = 0
        self._data = bytes()


class Kcp:
    def __init__(self):
        self._mtu = KCP_MTU_DEF
        self._mss = self._mtu - KCP_OVERHEAD
        self._state = 0

        self._snd_una = 0
        self._snd_nxt = 0
        self._rcv_nxt = 0

        self._ts_recent = 0
        self._ts_lastack = 0
        self._ssthresh = KCP_THRESH_INIT

        self._rx_rttval = 0
        self._rx_srtt = 0
        self._rx_rto = KCP_RTO_DEF
        self._rx_minrto = KCP_RTO_MIN

        self._snd_wnd = KCP_WND_SND
        self._rcv_wnd = KCP_WND_RCV
        self._rmt_wnd = KCP_WND_RCV
        self._cwnd = 0
        self._probe = 0

        self._current = 0
        self._interval = KCP_INTERVAL
        self._ts_flush = KCP_INTERVAL
        self._xmit = 0

        self._nrcv_buf = 0
        self._nsnd_buf = 0

        self._nodelay = 0
        self._updated = 0

        self._ts_probe = 0
        self._probe_wait = 0

        self._dead_link = KCP_DEADLINK
        self._incr = 0

        self._snd_queue = []
        self._rcv_queue = []

        self._snd_buf = []
        self._rcv_buf = []

        self._acklist = []
        self._ackcount = 0
        self._ackblock = 0
        self._fastresend = 0
        self._nocwnd = 0
        self._stream = 0

        self._output_cb = None
        self._recv_cb = None

    def set_output_cb(self, output_cb):
        self._output_cb = output_cb

    def set_recv_cb(self, recv_cb):
        self._recv_cb = recv_cb

    def recv(self, size):
        ispeek = False
        if size == 0:
            return 0
        elif size < 0:
            ispeek = True
            size = -size

        if len(self._rcv_queue) <= 0:
            return -1

        peeksize = self.peeksize()
        if peeksize < 0:
            return -2
        elif peeksize > size:
            return -3

        recover = False
        if len(self._rcv_queue) >= self._rcv_wnd:
            recover = True

        data = bytes()
        start = 0
        for start in range(len(self._rcv_queue)):
            segment = self._rcv_queue[start]
            data += segment.get_data()
            if segment.get_frg() == 0:
                break
        if ispeek:
            self._rcv_queue = self._rcv_queue[start:]

        while len(self._rcv_buf) > 0:
            segment = self._rcv_buf[0]
            if segment.get_sn() != self._rcv_nxt:
                break
            if len(self._rcv_queue) >= self._rcv_wnd:
                break
            self._rcv_queue.append(segment)
            self._rcv_buf.pop(0)
            self._rcv_nxt = u32_next(self._rcv_nxt)

        if recover and self._rcv_queue < self._rcv_wnd:
            self._probe |= KCP_ASK_TELL

        return data

    def peeksize(self):
        if len(self._rcv_queue) <= 0:
            return -1
        segment = self._rcv_queue[0]
        if segment.get_frg() == 0:
            return len(segment.get_data())
        if len(self._rcv_queue) < segment.get_frg() + 1:
            return -1

        size = 0
        for segment in self._rcv_queue:
            size += len(segment.get_data())
            if segment.get_frg() == 0:
                break
        return size

    def send(self, data):
        if self._stream:
            if len (self._snd_queue) > 0:
                segment = self._snd_queue[0]
                if len(segment.get_data()) < self._mss:
                    capacity = self._mss - len(segment.get_data())
                    segment.append_data(data[:capacity])
                    data = data[capacity:]
                    if len(data) <= 0:
                        return 0

        count = 0
        if len(data) <= self._mss:
            count = 1
        else:
            count = (len + self._mss - 1) / self._mss

        if count > 255:
            return -2
        for i in range(count):
            segment = KcpSegment()
            segment.set_frg(0 if self._stream else (count - 1 - i))
            segment.append_data(data[:self._mss])
            data = data[self._mss:]
            self._snd_queue.push(segment)
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
