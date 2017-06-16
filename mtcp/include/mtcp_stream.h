#ifndef __MTCP_STREAM_H__
#define __MTCP_STREAM_H__

#include "mtcp_segment.h"
#include <list>
#include <utility>

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

    void update_time(int64_t cur_time);

    int send(const char *buf, int len);
    int recv(const char *buf, int len);
    void update(int64_t cur_time);
    int64_t next_update_time();
private:
    uint16_t _mtu;
    uint16_t _mss;
    uint32_t _send_una;
    uint32_t _send_next;
    uint32_t _recv_next;
    uint16_t _cwnd;

    uint16_t _recv_wnd;
    MTcpBuffer _recv_cache;

    uint16_t _send_wnd;
    std::list<MTcpSegment*> _send_cache;
    std::list<MTcpSegment*> _send_queue;

    int64_t _last_time;
    uint32_t _ts;
    uint32_t _interval;

    FnSend _send_cb;
    void *_send_param;
    FnRecv _recv_cb;
    void *_recv_param;
    FnError _error_cb;
    void *_error_param;
};

#endif
