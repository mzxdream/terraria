#ifndef _MTCP_BUFFER_H_
#define _MTCP_BUFFER_H_

#include "mtcp_internal.h"
#include <list>

#define MTCP_HEADER_MAX 60

class MTcpBuffer
{
public:
    explicit MTcpBuffer(std::size_t = 0);
    ~MTcpBuffer();
private:
    MTcpBuffer(const MTcpBuffer &);
    MTcpBuffer& operator=(const MTcpBuffer &);
public:
    static MTcpBuffer* unserialize(const char *, std::size_t);
public:
    const char* serialize(std::size_t * = 0);
    const char* data(std::size_t * = 0);
    std::size_t len();
    MTcpHeader& header();

    std::size_t read(const char *, std::size_t);
    std::size_t append(const char *, std::size_t);
private:
    char *_buf;
    char *_head;
    char *_data;
    char *_tail;
    char *_end;
    MTcpHeader _th;
};

#endif
