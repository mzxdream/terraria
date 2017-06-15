#include "mtcp_buffer.h"
#include <algorithm>

MTcpBuffer::MTcpBuffer()
    :_buf(0)
    ,_begin(0)
    ,_size(0)
    ,_capacity(0)
{
}

MTcpBuffer::MTcpBuffer(std::size_t size)
    :_buf(0)
    ,_begin(0)
    ,_size(0)
    ,_capacity(0)
{
    resize(size);
}

MTcpBuffer::MTcpBuffer(const char *buf, std::size_t size)
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

const char* MTcpBuffer::buffer(std::size_t *size) const
{
    if (size)
    {
        *size = _size;
    }
    return _begin;
}

std::size_t MTcpBuffer::size() const
{
    return _size;
}

void MTcpBuffer::resize(std::size_t size)
{
    if (size > _capacity)
    {
        _capacity = next_power_2(size);
        char *tmp = new char[_capacity]();
        std::copy(_begin, _begin + _size, tmp);
        delete[] _buf;
        _begin = _buf = tmp;
    }
    else if (size > _capacity - (_begin - _buf))
    {
        std::copy(_begin, _begin + _size, _buf);
        _begin = _buf;
    }
    _size = size;
}

void MTcpBuffer::shrink(std::size_t size)
{
    if (size > _size)
    {
        size = _size;
    }
    _begin += size;
    _size -= size;
}

void MTcpBuffer::append(const char *buf, std::size_t size)
{
    if (!buf || size <= 0)
    {
        return;
    }
    resize(_size + size);
    std::copy(buf, buf + size, _begin + _size);
    _size += size;
}

void MTcpBuffer::write(const char *buf, std::size_t size, std::size_t begin)
{
    if (!buf || size <= 0)
    {
        return;
    }
    resize(begin + size);
    std::copy(buf, buf + size, _begin + begin);
    _size = begin + size;
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

std::size_t MTcpBuffer::read(char *buf, std::size_t size, std::size_t begin) const
{
    if (!buf || size <= 0 || _size <= 0)
    {
        return 0;
    }
    if (begin >= _size)
    {
        return 0;
    }
    if (begin + size > _size)
    {
        size = _size - begin;
    }
    std::copy(_begin + begin, _begin + begin + size, buf);
    return size;
}
