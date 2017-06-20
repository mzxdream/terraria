#ifndef _MTCP_BUFFER_H_
#define _MTCP_BUFFER_H_

#include "mtcp_internal.h"
#include <vector>

#define MTCP_SACK_MAX 10
#define MTCP_HEADER_MAX (24 + 4 * MTCP_SACK_MAX)

class MTcpBuffer
{
public:
    explicit MTcpBuffer(uint16_t capacity);
    ~MTcpBuffer();
private:
    MTcpBuffer(const MTcpBuffer &);
    MTcpBuffer& operator=(const MTcpBuffer &);
public:
    static bool decode(const char *data, uint16_t size, MTcpBuffer *buf);
    const char* encode(uint16_t *size) const;
public:
    uint32_t seq() const;
    uint32_t ack_seq() const;
    uint32_t ts() const;
    uint32_t ack_ts() const;
    uint16_t cmd() const;
    uint16_t wnd() const;
    uint16_t len() const;
    const std::vector<uint32_t>& sacks() const;

    void seq(uint32_t);
    void ack_seq(uint32_t);
    void ts(uint32_t);
    void ack_ts(uint32_t);
    void cmd(uint16_t);
    void wnd(uint16_t);
    bool append_sack(uint32_t);
public:
    uint16_t append(const char *data, uint16_t size);
    uint16_t peek(char *data, uint16_t size) const;
    uint16_t get(char *data, uint16_t size);
private:
    char *_buf;
    char *_data;
    uint16_t _capacity;

    uint32_t _seq;
    uint32_t _ack_seq;
    uint32_t _ts;
    uint32_t _ack_ts;
    uint16_t _cmd;
    uint16_t _wnd;
    uint16_t _len;
    std::vector<uint32_t> _sacks;
};

#endif
