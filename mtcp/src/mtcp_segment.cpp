#include "mtcp_segment.h"

#define MTCP_SEGMENT_HEAD_LEN 24

MTcpSegment::MTcpSegment()
    :_buf(MTCP_SEGMENT_HEAD_LEN)
    ,_len(0)
    ,_skip(0)
{
}

uint32_t MTcpSegment::seq() const
{
    uint32_t seq = 0;
    _buf.read(seq, 0);
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


uint32_t MTcpSegment::ack() const
{
    uint32_t ack = 0;
    _buf.read(ack, 8);
    return ack;
}

void MTcpSegment::ack(uint32_t ack)
{
    _buf.write(ack, 8);
}

uint32_t MTcpSegment::ts() const
{
    uint32_t ts = 0;
    _buf.read(ts, 12);
    return ts;
}

void MTcpSegment::ts(uint32_t ts)
{
    _buf.write(ts, 12);
}

uint16_t MTcpSegment::wnd() const
{
    uint16_t wnd = 0;
    _buf.read(wnd, 16);
    return wnd;
}

void MTcpSegment::wnd(uint16_t wnd)
{
    _buf.write(wnd, 16);
}

uint16_t MTcpSegment::cmd() const
{
    uint16_t cmd = 0;
    _buf.read(cmd, 18);
    return cmd;
}

void MTcpSegment::cmd(uint16_t cmd)
{
    _buf.write(cmd, 18);
}

void MTcpSegment::append_data(const char *buf, uint32_t size)
{
    _buf.write(buf, size, _len);
    _len += size;
}

uint32_t MTcpSegment::get_data(char *buf, uint32_t size)
{

}

uint32_t MTcpSegment::
