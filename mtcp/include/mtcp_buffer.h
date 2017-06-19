#ifndef _MTCP_BUFFER_H_
#define _MTCP_BUFFER_H_

#include "mtcp_internal.h"

class MTcpBuffer
{
public:
    MTcpBuffer();
    explicit MTcpBuffer(std::size_t capacity);
    ~MTcpBuffer();
private:
    MTcpBuffer(const MTcpBuffer &);
    MTcpBuffer& operator=(const MTcpBuffer &);
public:
    void size(std::size_t size);
    std::size_t size() const;
    void lshrink(std::size_t size);
    void rshrink(std:;size_t size);
    bool capacity(std::size_t capacity);
    std::size_t capacity() const;

    std::size_t append(const char *buf, std::size_t size);
    template <typename T>
    bool append(T val)
    {
        if (_capacity < _size + sizeof(val))
        {
            return false;
        }
        val = hton_any(val);
        append(reinterpret_cast<const char*>(&val), sizeof(val));
        return true;
    }

    std::size_t peek(char *buf, std::size_t size) const;
    template <typename T>
    bool peek(T &val) const
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
        lshrink(sizeof(val));
        return true;
    }
private:
    char *_buf;
    char *_begin;
    std::size_t _size;
    std::size_t _capacity;
};

#endif
