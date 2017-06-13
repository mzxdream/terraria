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
    if (size > _capacity - _size)
    {
        _capacity = next_power_2(size + _size);
        char *tmp = new char[_capacity];
        std::copy(_begin, _begin + _size, tmp);
        delete[] _buf;
        _begin = _buf = tmp;
    }
    else if (size > _capacity - _size - (_begin - _buf))
    {
        std::copy(_begin, _begin + _size, _buf);
        _begin = _buf;
    }
    std::copy(buf, buf + size, _begin + _size);
    _size += size;
}

void MTcpBuffer::write(const char *buf, std::size_t size, std::size_t begin)
{
    if (!buf || size <= 0)
    {
        return;
    }
    if (size > _capacity - begin)
    {
        _capacity = next_power_2(size + begin);
        char *tmp = new char[_capacity];
        std::copy(_begin, _begin + _size, tmp);
        delete[] _buf;
        _begin = _buf = tmp;
    }
    else if (size > _capacity - begin - (_begin - _buf))
    {
        std::copy(_begin, _begin + _size, _buf);
        _begin = _buf;
    }
    std::copy(buf, buf + size, _begin + begin);
    _size = begin + size;
}

std::size_t MTcpBuffer::peek(char *buf, std::size_t size)
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

std::size_t MTcpBuffer::read(char *buf, std::size_t size, std::size_t begin)
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
