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

    bool append(const char *buf, std::size_t size);
    template <typename T>
    bool append(T val)
    {
        val = hton_any(val);
        return append(reinterpret_cast<const char*>(&val), sizeof(val));
    }

    std::size_t peek(char *buf, std::size_t size);
    template <typename T>
    bool peek(T &val)
    {
        std::size_t size = sizeof(val);
        if (peek(reinterpret_cast<char*>(&val), size) != size)
        {
            return false;
        }
        val = ntoh_any(val);
        return true;
    }

    std::size_t get(char *buf, std::size_t size);
    template <typename T>
    bool get(T &val)
    {
        if (!peek(val))
        {
            return false;
        }
        _begin += sizeof(val);
        return true;
    }
private:
    char *_buf;
    char *_begin;
    std::size_t _size;
    std::size_t _capacity;
};

#endif
