#ifndef _MTCP_BUFFER_H_
#define _MTCP_BUFFER_H_

#include "mtcp_internal.h"
#include <list>

#define MTCP_SACK_MAX (10 * 4)
#define MTCP_HEADER_MAX 24

class MTcpBuffer
{
public:
    explicit MTcpBuffer(uint16_t);
    ~MTcpBuffer();
private:
    MTcpBuffer(const MTcpBuffer &);
    MTcpBuffer& operator=(const MTcpBuffer &);
public:
    static bool decode(const char*, uint16_t, MTcpBuffer*);
    const char* encode(uint16_t*) const;
public:
    uint32_t seq() const;
    uint32_t ack_seq() const;
    uint32_t ts() const;
    uint32_t ack_ts() const;
    uint16_t cmd() const;
    uint16_t wnd() const;
    uint16_t len() const;
    uint16_t size() const;//include header size
    const std::list<uint32_t>& sacks() const;

    void seq(uint32_t);
    void ack_seq(uint32_t);
    void ts(uint32_t);
    void ack_ts(uint32_t);
    void cmd(uint16_t);
    void wnd(uint16_t);
    bool append_sack(uint32_t);
public:
    uint16_t append(const char*, uint16_t);
    uint16_t peek(char*, uint16_t) const;
    uint16_t get(char*, uint16_t);
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
    std::list<uint32_t> _sacks;
};

#endif
