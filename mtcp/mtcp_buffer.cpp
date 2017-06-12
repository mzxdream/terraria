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

int MTcpBuffer::append(char *buf, std::size_t size)
{
    if (!buf || size < 0)
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
    else if (size > _capacity - size - (_begin - _buf)) {
        std::copy(_begin, _begin + _size, _buf);
        _begin = _buf;
    }
    std::copy(buf, buf + size, _begin + _size);
    _size += size;
    return 0;
}
