#include "mtcp_buffer.h"
#include <algorithm>

MTcpBuffer::MTcpBuffer(std::size_t capacity)
    :_buf(0)
    ,_data(0)
    ,_capacity(0)
    ,_seq(0)
    ,_ack_seq(0)
    ,_ts(0)
    ,_ack_ts(0)
    ,_cmd(0)
    ,_wnd(0)
    ,_len(0)
{
    _capacity = MTCP_HEADER_MAX + capacity;
    _buf = new char[_capacity]();
    if (_buf)
    {
        _data = _buf + MTCP_HEADER_MAX;
    }
}

MTcpBuffer::~MTcpBuffer()
{
    if (_buf)
    {
        delete[] _buf;
        _buf = 0;
    }
}

bool MTcpBuffer::decode(const char *data, uint16_t size, MTcpBuffer *buf)
{
    if (!buf)
    {
        return false;
    }
    return true;
}

const char* MTcpBuffer::encode(uint16_t *size) const
{
    return 0;
}



std::size_t MTcpBuffer::append(const char *buf, std::size_t size)
{
    if (!buf || size <= 0 || _capacity <= _size)
    {
        return 0;
    }
    if (size + _size > _capacity)
    {
        size = _capacity - _size;
    }
    std::size_t right = _begin - _buf + _size;
    if (right >= _capacity)
    {
        std::copy(buf, buf + size, _buf + (right - _capacity));
    }
    else if (right + size > _capacity)
    {
        std::size_t copied = _capacity - right;
        std::copy(buf, buf + copied, _begin + _size);
        std::copy(buf + copied, buf + size, _buf);
    }
    else
    {
        std::copy(buf, buf + size, _begin + _size);
    }
    _size += size;
    return size;
}

std::size_t MTcpBuffer::peek(char *buf, std::size_t size) const
{
    if (!buf || size <= 0 || _size <= 0)
    {
        return 0;
    }
    if (size > _size)
    {
        size = _size;
    }
    if (_begin - _buf + size > _capacity)
    {
        std::size_t copied = _capacity - (_begin - _buf);
        std::copy(_begin, _begin + copied, buf);
        std::copy(_buf, _buf + (size - copied), buf + copied);
    }
    else
    {
        std::copy(_begin, _begin + size, buf);
    }
    return size;
}

std::size_t MTcpBuffer::get(char *buf, std::size_t size)
{
    size = peek(buf, size);
    if (size > 0)
    {
        lshrink(size);
    }
    return size;
}
