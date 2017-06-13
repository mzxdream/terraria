#include "mtcp_buffer.h"
#include <algorithm>

MTcpBuffer::MTcpBuffer()
    :_buf(0)
    ,_begin(0)
    ,_size(0)
    ,_capacity(0)
{
}

MTcpBuffer::MTcpBuffer(char *buf, std::size_t size)
    :_buf(0)
    ,_begin(0)
    ,_size(0)
    ,_capacity(0)
{
    append(buf, size);
}

MTcpBuffer::~MTcpBuffer()
{
    if (_buf) {
        delete[] _buf;
        _buf = 0;
    }
}

const char* MTcpBuffer::buffer() const
{
    return _buf;
}

const char* MTcpBuffer::buffer(std::size_t &size) const
{
    size = _size;
    return _buf;
}

std::size_t MTcpBuffer::size() const
{
    return _size;
}

bool MTcpBuffer::append(const char *buf, std::size_t size)
{
    if (!buf || size <= 0)
    {
        return false;
    }
    if (size > _capacity - _size)
    {
        _capacity = next_power_2(size + _size);
        char *tmp = new char[_capacity];
        std::copy(_begin, _begin + _size, tmp);
        delete[] _buf;
        _begin = _buf = tmp;
    }
    else if (size > _capacity - _size - (_begin - _buf)) {
        std::copy(_begin, _begin + _size, _buf);
        _begin = _buf;
    }
    std::copy(buf, buf + size, _begin + _size);
    _size += size;
    return true;
}

std::size_t MTcpBuffer::peek(char *buf, std::size_t size)
{
    if (size <= 0 || _size <= 0)
    {
        return 0;
    }
    if (size > _size)
    {
        size = _size;
    }
    std::copy(_begin, _begin + size, buf);
    return size;
}

std::size_t MTcpBuffer::get(char *buf, std::size_t size)
{
    size = peek(buf, size);
    if (size > 0)
    {
        _begin += size;
    }
    return size;
}
