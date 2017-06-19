#include "mtcp_stream.h"

MTcpStream::MTcpStream()
{
}

MTcpStream::~MTcpStream()
{
}

void MTcpStream::send_cb(FnSend send_cb, void *param)
{
    _send_cb = send_cb;
    _send_param = param;
}

void MTcpStream::recv_cb(FnRecv recv_cb, void *param)
{
    _recv_cb = recv_cb;
    _recv_param = param;
}

void MTcpStream::update_time(int64_t cur_time)
{
    int64_t diff = cur_time - _last_time;
    if (diff < 0 || diff > 10 * _interval)
    {
        diff = _interval;
    }
    _last_time = cur_time;
    _ts += diff;
}

int MTcpStream::send(const char *buf, int len)
{
    if (!buf || len <= 0)
    {
        return 0;
    }
    return _send_buf.append(buf, len);
}

int MTcpStream::recv(const char *buf, int len, int64_t cur_time)
{
    update_time(cur_time);
    if (!decode_tcp_header(buf, len, &_header))
    {
        return -1;
    }
    return 0;
}

void MTcpStream::update(int64_t cur_time)
{
    update_time(cur_time);
}

int64_t next_update_time(int64_t cur_time)
{
    update_time(cur_time);
}
