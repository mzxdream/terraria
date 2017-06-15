#ifndef _MTCP_BUFFER_H_
#define _MTCP_BUFFER_H_

#include "mtcp_internal.h"

class MTcpBuffer
{
public:
    MTcpBuffer();
    explicit MTcpBuffer(std::size_t size);
    explicit MTcpBuffer(const char *buf, std::size_t size);
    ~MTcpBuffer();
private:
    MTcpBuffer(const MTcpBuffer &);
    MTcpBuffer& operator=(const MTcpBuffer &);
public:
    const char* buffer(std::size_t *size = 0) const;
    std::size_t size() const;
    void resize(std::size_t size);
    void shrink(std::size_t size);

    void append(const char *buf, std::size_t size);
    template <typename T>
    void append(T val)
    {
        val = hton_any(val);
        append(reinterpret_cast<const char*>(&val), sizeof(val));
    }

    void write(const char *buf, std::size_t size, std::size_t begin = 0);
    template <typename T>
    void write(T val, std::size_t begin = 0)
    {
        val = hton_any(val);
        write(reinterpret_cast<const char*>(&val), sizeof(val), begin);
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
        _begin += sizeof(val);
        return true;
    }

    std::size_t read(char *buf, std::size_t size, std::size_t begin = 0) const;
    template <typename T>
    bool read(T &val, std::size_t begin = 0) const
    {
        std::size_t size = sizeof(val);
        if (read(reinterpret_cast<char*>(&val), size, begin) != size)
        {
            return false;
        }
        val = ntoh_any(val);
        return true;
    }
private:
    char *_buf;
    char *_begin;
    std::size_t _size;
    std::size_t _capacity;
};

#endif
