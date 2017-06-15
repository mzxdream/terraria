#ifndef _MTCP_SEGMENT_H_
#define _MTCP_SEGMENT_H_

#include "mtcp_buffer.h"

#define MTCP_SEGMENT_HEAD_LEN 24

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
    uint32_t ts() const;
    void ts(uint32_t ts);
    uint16_t wnd() const;
    void wnd(uint16_t wnd);
    uint16_t cmd() const;
    void cmd(uint16_t cmd);
    uint16_t len() const;
private:
    void len(uint16_t len);
public:
    const char* data(uint16_t *len);
    uint16_t buffer_len() const;
    const char* buffer(uint16_t *len);
    void append_data(const char *buf, uint16_t len);
private:
    MTcpBuffer _buf;
};

#endif
