#ifndef __MTCP_STREAM_H__
#define __MTCP_STREAM_H__

#include "mtcp_buffer.h"
#include <list>
#include <utility>
#include <string>

#define MTCP_CMD_ACK  0x01
#define MTCP_CMD_PUSH 0x02

#define MTCP_EVENT_RECV 0x01
#define MTCP_EVENT_ERROR 0x02

class MTcpStream
{
    typedef void (*FnOutput)(const char*, std::size_t, void*);
    typedef void (*FnEvent)(int, void *);
public:
    MTcpStream();
    ~MTcpStream();
private:
    MTcpStream(const MTcpStream &);
    MTcpStream& operator=(const MTcpStream &);
public:
    void output_cb(FnOutput output_cb, void *param = 0);
    void event_cb(FnEvent event_cb, void *param = 0);

    int send(const char *buf, int len, int64_t cur_time);
    int input(const char *buf, int len, int64_t cur_time);
    int recv(char *buf, int len, int64_t cur_time);
    void update_time(int64_t cur_time);
    void update(int64_t cur_time);
    int64_t next_update_time(int64_t cur_time);
private:
    uint16_t _mtu;
    uint16_t _mss;
    uint32_t _send_una;
    uint32_t _send_next;
    uint32_t _recv_next;
    uint16_t _cwnd;

    uint16_t _recv_wnd;
    uint32_t _recv_len;
    std::list<MTcpBuffer*> _recv_list;
    std::list<MTcpBuffer*> _recv_

    uint16_t _send_wnd;
    uint32_t _send_len;
    std::list<MTcpBuffer*> _send_list;

    int64_t _last_time;
    uint32_t _ts;
    uint32_t _interval;

    FnSend _send_cb;
    void *_send_param;
    FnRecv _recv_cb;
    void *_recv_param;
    int _last_error;
};

#endif
