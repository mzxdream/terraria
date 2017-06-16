#include "mtcp_segment.h"

MTcpSegment::MTcpSegment()
    :_buf(MTCP_SEGMENT_HEAD_LEN)
{
}

uint32_t MTcpSegment::seq() const
{
    uint32_t seq = 0;
    _buf.read(seq, std::size_t(0));
    return seq;
}

void MTcpSegment::seq(uint32_t seq)
{
    _buf.write(seq, 0);
}

uint32_t MTcpSegment::una() const
{
    uint32_t una = 0;
    _buf.read(una, 4);
    return una;
}

void MTcpSegment::una(uint32_t una)
{
    _buf.write(una, 4);
}

uint32_t MTcpSegment::ts() const
{
    uint32_t ts = 0;
    _buf.read(ts, 8);
    return ts;
}

void MTcpSegment::ts(uint32_t ts)
{
    _buf.write(ts, 8);
}

uint16_t MTcpSegment::wnd() const
{
    uint16_t wnd = 0;
    _buf.read(wnd, 12);
    return wnd;
}

void MTcpSegment::wnd(uint16_t wnd)
{
    _buf.write(wnd, 12);
}

uint16_t MTcpSegment::cmd() const
{
    uint16_t cmd = 0;
    _buf.read(cmd, 14);
    return cmd;
}

void MTcpSegment::cmd(uint16_t cmd)
{
    _buf.write(cmd, 14);
}

uint16_t MTcpSegment::len() const
{
    uint16_t len = 0;
    _buf.read(len, 16);
    return len;
}

void MTcpSegment::len(uint16_t len)
{
    _buf.write(len, 16);
}

const char* MTcpSegment::data(uint16_t *len)
{
    if (len)
    {
        *len = this->len();
    }
    return _buf.buffer() + MTCP_SEGMENT_HEAD_LEN;
}

uint16_t MTcpSegment::buffer_len() const
{
    return MTCP_SEGMENT_HEAD_LEN + len();
}

const char* MTcpSegment::buffer(uint16_t *len)
{
    if (len)
    {
        *len = this->buffer_len();
    }
    return _buf.buffer();
}

void MTcpSegment::append_data(const char *buf, uint16_t len)
{
    _buf.write(buf, len, buffer_len());
    this->len(this->len() + len);
}
