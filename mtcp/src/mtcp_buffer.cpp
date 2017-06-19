#include "mtcp_buffer.h"
#include <algorithm>

MTcpBuffer::MTcpBuffer()
    :_buf(0)
    ,_begin(0)
    ,_size(0)
    ,_capacity(0)
{
}

MTcpBuffer::MTcpBuffer(std::size_t capacity)
    :_buf(0)
    ,_begin(0)
    ,_size(0)
    ,_capacity(0)
{
    _begin = _buf = new char[capacity]();
    _capacity = capacity;
}

MTcpBuffer::~MTcpBuffer()
{
    if (_buf)
    {
        delete[] _buf;
    }
    _begin = _buf = 0;
    _size = _capacity = 0;
}

void MTcpBuffer::size(std::size_t size)
{
    if (size > _capacity)
    {
        _size = _capacity;
    }
    else
    {
        _size = size;
    }
}

std::size_t MTcpBuffer::size() const
{
    return _size;
}

void MTcpBuffer::lshrink(std::size_t size)
{
    if (size > _size)
    {
        _size = 0;
    }
    else
    {
        _size -= size;
        _begin += size;
        if (_begin >= _buf + _capacity)
        {
            _begin -= _capacity;
        }
    }
}

void MTcpBuffer::rshrink(std::size_t size)
{
    if (size > _size)
    {
        _size = 0;
    }
    else
    {
        _size -= size;
    }
}

bool MTcpBuffer::capacity(std::size_t capacity)
{
    if (_capacity == capacity)
    {
        return true;
    }
    if (capacity == 0)
    {
        delete _buf;
        _begin = _buf = 0;
        _size = _capacity = 0;
        return true;
    }
    char *buf = new char[capacity]();
    if (!buf)
    {
        return false;
    }
    _size = peek(buf, capacity);
    delete[] _buf;
    _capacity = capacity;
    _begin = _buf = buf;
}

std::size_t MTcpBuffer::capacity() const
{
    return _capacity;
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
