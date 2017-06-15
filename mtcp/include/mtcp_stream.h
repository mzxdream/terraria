#ifndef __MTCP_STREAM_H__
#define __MTCP_STREAM_H__

#include "mtcp_segment.h"

class MTcpStream
{
    typedef void (*FnSend)(const char *buf, int len, void *param);
    typedef void (*FnRecv)(const char *buf, int len, void *param);
    typedef void (*FnError)(int error, void *param);
public:
    MTcpStream();
    ~MTcpStream();
private:
    MTcpStream(const MTcpStream &);
    MTcpStream& operator=(const MTcpStream &);
public:
    void send_cb(FnSend send_cb, void *param = 0);
    void recv_cb(FnRecv recv_cb, void *param = 0);
    void error_cb(FnError error_cb, void *param = 0);

    int send(const char *buf, int len, int64_t cur_time);
    int recv(const char *buf, int len, int64_t cur_time);
    void update(int64_t cur_time);
    int64_t next_update_time(int64_t cur_time);
private:
    uint16_t _mtu;
    uint32_t _send_una;
    uint32_t _send_next;
    uint32_t _recv_next;

    int64_t start

    FnSend _send_cb;
    void *_send_param;
    FnRecv _recv_cb;
    void *_recv_param;
};

#endif
