#ifndef _MTCP_BUFFER_H_
#define _MTCP_BUFFER_H_

#include "mtcp_internal.h"

class MTcpBuffer
{
public:
    MTcpBuffer();
    explicit MTcpBuffer(char *buf, std::size_t size);
    ~MTcpBuffer();
private:
    MTcpBuffer(const MTcpBuffer &);
    MTcpBuffer& operator=(const MTcpBuffer &);
public:
    const char* buffer() const;
    const char* buffer(std::size_t &size) const;
    std::size_t size() const;
    int append(const char *buf, std::size_t size);
    template<typename T>
    int append(T val);
private:
    char *_buf;
    char *_begin;
    std::size_t _size;
    std::size_t _capacity;
};

#endif
