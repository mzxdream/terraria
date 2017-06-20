#include "mtcp_buffer.h"
#include <algorithm>

MTcpBuffer::MTcpBuffer(uint16_t capacity)
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
    if (capacity >= MTCP_HEADER_MAX)
    {
        _capacity = capacity;
        _buf = new char[_capacity + MTCP_SACK_MAX]();
        if (_buf)
        {
            _data = _buf + MTCP_HEADER_MAX + MTCP_SACK_MAX;
        }
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
    if (!data || size < MTCP_HEADER_MAX || !buf)
    {
        return 0;
    }
    data = decode_any(data, buf->_seq);
    data = decode_any(data, buf->_ack_seq);
    data = decode_any(data, buf->_ts);
    data = decode_any(data, buf->_ack_ts);
    data = decode_any(data, buf->_cmd);
    data = decode_any(data, buf->_wnd);
    data = decode_any(data, buf->_len);
    uint16_t sack_len = 0;
    data = decode_any(data, sack_len);
    if (size != MTCP_HEADER_MAX + sack_len * 4 + buf->_len)
    {
        return false;
    }
    if (MTCP_HEADER_MAX + buf->_len > buf->_capacity)
    {
        return false;
    }
    for (uint16_t i = 0; i < sack_len; ++i)
    {
        uint32_t sack = 0;
        data = decode_any(data, sack);
        buf->_sacks.push_back(sack);
    }
    //TODO
    return true;
}

const char* MTcpBuffer::encode(uint16_t *size) const
{
    return 0;
}

uint32_t MTcpBuffer::seq() const
{
    return _seq;
}

uint32_t MTcpBuffer::ack_seq() const
{
    return _ack_seq;
}

uint32_t MTcpBuffer::ts() const
{
    return _ts;
}

uint32_t MTcpBuffer::ack_ts() const
{
    return _ack_ts;
}

uint16_t MTcpBuffer::cmd() const
{
    return _cmd;
}

uint16_t MTcpBuffer::wnd() const
{
    return _wnd;
}

uint16_t MTcpBuffer::len() const
{
    return _len;
}

uint16_t MTcpBuffer::size() const
{
    return _len + MTCP_HEADER_MAX + 4 * _sacks.size();
}

const std::list<uint32_t>& MTcpBuffer::sacks() const
{
    return _sacks;
}

void MTcpBuffer::seq(uint32_t seq)
{
    _seq = seq;
}

void MTcpBuffer::ack_seq(uint32_t ack_seq)
{
    _ack_seq = ack_seq;
}

void MTcpBuffer::ts(uint32_t ts)
{
    _ts = ts;
}

void MTcpBuffer::ack_ts(uint32_t ack_ts)
{
    _ack_ts = ack_ts;
}

void MTcpBuffer::cmd(uint16_t cmd)
{
    _cmd = cmd;
}

void MTcpBuffer::wnd(uint16_t wnd)
{
    _wnd = wnd;
}

bool MTcpBuffer::append_sack(uint32_t sack)
{
    if (_sacks.size() * 4 >= MTCP_SACK_MAX)
    {
        return false;
    }
    if (this->size() + 4 > _capacity)
    {
        return false;
    }
    _sacks.push_back(sack);
    return true;
}

uint16_t MTcpBuffer::append(const char *data, uint16_t size)
{
    if (!data || size <= 0 || _capacity <= this->size())
    {
        return 0;
    }
    size = std::min(size, _capacity - this->size());
    if (_data + _len + size > _buf + _capacity + 2 * MTCP_SACK_MAX)
    {
        char *ptr = _buf + MTCP_HEADER_MAX + MTCP_SACK_MAX;
        std::copy(_data, _data + _len, ptr);
        _data = ptr;
    }
    std::copy(data, data + size, _data + _len);
    return size;
}

uint16_t MTcpBuffer::peek(char *data, uint16_t size) const
{
    if (size <= 0 || _len <= 0)
    {
        return 0;
    }
    size = std::min(size, _len);
    if (data)
    {
        std::copy(_data, _data + size, data);
    }
    return size;
}

uint16_t MTcpBuffer::get(char *data, uint16_t size)
{
    if (size <= 0 || _len <= 0)
    {
        return 0;
    }
    size = std::min(size, _len);
    if (data)
    {
        std::copy(_data, _data + size, data);
    }
    return size;
}
