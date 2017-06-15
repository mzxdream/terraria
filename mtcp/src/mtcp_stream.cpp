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

int MTcpStream::send(const char *buf, int len, int64_t cur_time)
{
    return 0;
}

int MTcpStream::recv(const char *buf, int len, int64_t cur_time)
{
    return 0;
}

void MTcpStream::update()
{
}

int64_t next_update_time(int64_t cur_time)
{
}
