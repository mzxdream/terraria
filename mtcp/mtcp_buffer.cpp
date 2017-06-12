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

int MTcpBuffer::append(const char *buf, std::size_t size)
{
    if (!buf || size <= 0)
    {
        return -1;
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
    return 0;
}

template <typename T>
int MTcpBuffer::append(T val)
{
    val = hton_any(val);
    return append(reinterpret_cast<char*>(&val), sizeof(val));
}
