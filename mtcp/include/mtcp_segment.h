#ifndef _MTCP_SEGMENT_H_
#define _MTCP_SEGMENT_H_

#include "mtcp_buffer.h"

class MTcpSegment
{
public:
    MTcpSegment();
    ~MTcpSegment();
private:
    MTcpSegment(const MTcpSegment &);
    MTcpSegment& operator=(const MTcpSegment &);
public:
    uint32_t seq() const;
    void seq(uint32_t seq);
    uint32_t una() const;
    void una(uint32_t una);
    uint32_t ack() const;
    void ack(uint32_t ack);
    uint32_t ts() const;
    void ts(uint32_t ts);
    uint16_t wnd() const;
    void wnd(uint16_t wnd);
    uint16_t cmd() const;
    void cmd(uint16_t cmd);
    void append_data(const char *buf, uint32_t size);
    const char* data(const char *buf, uint32_t size);
    const char* buffer(std::size_t *size = 0);

    uint32_t incr_skip();
    uint32_t get_skip() const;
private:
    MTcpBuffer _buf;
    uint32_t _len;
    uint32_t _skip;
};

#endif
