#include "mtcp_stream.h"

MTcpStream::MTcpStream()
{
}

MTcpStream::~MTcpStream()
{
}

void MTcpStream::set_send_cb(FnSend send_cb, void *param)
{
    _send_cb = send_cb;
    _send_param = param;
}

void MTcpStream::set_recv_cb(FnRecv recv_cb, void *param)
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
    _ts += static_cast<uint32_t>(diff);
}

int MTcpStream::send(const char *buf, int len)
{
    if (!buf || len <= 0)
    {
        return 0;
    }
    int copy = 0;
    int copied = 0;
    if (!_send_cache.empty())
    {
        MTcpSegment *seg = _send_cache.back();
        if (!seg)
        {
            return -1;
        }
        copy = _mss - seg->len();
        if (copy > 0)
        {
            if (copy > len)
            {
                copy = len;
            }
            seg->append_data(buf, copy);
            copied += copy;
        }
    }
    while (copied < len
            && _send_queue.size() + _send_cache.size() < _send_wnd)
    {
        copy = len - copied;
        if (copy > _mss)
        {
            copy = _mss;
        }
        MTcpStream *seg = new MTcpSegment();
        if (!seg)
        {
            return -1;
        }
        seg->append_data(buf + copied, copy);
        copied += copy;
    }
    return copied;
}

int MTcpStream::recv(const char *buf, int len)
{
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
