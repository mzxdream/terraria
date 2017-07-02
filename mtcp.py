#!/usr/bin/env python
#code: utf-8

class MTcpBuffer:
    def __init__(self, data):
        pass
    def len(self):
        pass
    def append(self, data):
        pass
    def remove(self, len):
        pass
    def get_header(self):
        pass
    def get_data(self):
        pass

def parse_to_buffer(data):
    pass

class MTcpStream:
    def __init__(self):
        self._snd_buf_list = []
        self._snd_buf_cur = 0
        self._snd_buf_len = 0
        self._snd_buf_max = 0

        self._rcv_buf_list = []
        self._rcv_buf_len = 0
        self._rcv_buf_max = 0
        self._mss = 100

    def send(self, data):
        send_len = min(len(data), self._snd_buf_max - self._snd_buf_len)
        if send_len <= 0:
            return 0
        sent = 0
        if self._snd_buf_cur < len(self._snd_buf_list):
            buf = self._snd_buf_list[-1]
            if buf.len() < self._mss:
                sent = self._mss - buf.len()
                if sent > send_len:
                    sent = send_len
                buf.append(data[:sent])
        while sent < send_len:
            if send_len - sent < self._mss:
                self._snd_buf_list.extend(MTcpBuffer(data[sent: send_len]))
                break
            self._snd_buf_list.extend(MTcpBuffer(data[sent, sent + self._mss]))
            sent += self._mss
        self._snd_buf_len -= send_len
        return send_len

    def recv(self, recv_len):
        recv_len = min(recv_len, self._rcv_buf_len)
        if recv_len <= 0:
            return 0
        received = 0
        data = []
        while received < recv_len:
            buf = self._rcv_buf_list[0]
            if recv_len - received < buf.len():
                data.extend(buf.remove(recv_len - received))
                break
            data.extend(buf.get_data())
            self._rcv_buf_list.pop(0)
            received += buf.len()
        self._rcv_buf_len -= recv_len
        return recv_len

    def input(self, data):
        buf = parse_to_buffer(data)
        if buf is None:
            return -1
        header = buf.get_header()
        if header is None:
            return -1
        self._rmt_wnd = header.get_wnd()
        self.ack_seq = header.get_ack_seq()

    def update(self):
        pass

if __name__ == "__main__":
    pass
