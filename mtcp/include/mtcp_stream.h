#ifndef __MTCP_STREAM_H__
#define __MTCP_STREAM_H__

#include "mtcp_buffer.h"
#include <list>
#include <utility>
#include <string>

#define MTCP_CMD_ACK 1
#define MTCP_CMD_PUSH 2

typedef struct
{
    uint32_t seq;
    uint32_t ack;
    uint32_t ts;
    uint32_t ack_ts;
    uint16_t wnd;
    uint16_t cmd;
    //uint16_t len;
    //uint16_t sack;
    const char *data;
    std::list<std::pair<uint32_t, uint32_t> > sack_list;
}MTcpHeader;

bool decode_tcp_header(const char *buf, int len, MTcpHeader *header)
{
    if (!buf || len < MTCP_HEADER_MAX || !header)
    {
        return false;
    }
    buf = decode(buf, header->seq);
    buf = decode(buf, header->ack);
    buf = decode(buf, header->ts);
    buf = decode(buf, header->wnd);
    buf = decode(buf, header->cmd);
    buf = decode(buf, header->len);
    buf = decode(buf, header->sack);
    if (len != MTCP_HEADER_MAX + header->sack * 8 + header->len)
    {
        return false;
    }
    header->sack_list.clear();
    for (std::size_t i = 0; i < header->len; ++i)
    {
        uint32_t begin = 0, end = 0;
        buf = decode(buf, begin);
        buf = decode(buf, end);
        header->sack_list.push(std::make_pair(begin, end));
    }
    header->data = buf;
    return true;
}


class MTcpStream
{
    typedef void (*FnSend)(const char*, std::size_t, void*);
    typedef void (*FnRecv)(int, void *);
public:
    MTcpStream();
    ~MTcpStream();
private:
    MTcpStream(const MTcpStream &);
    MTcpStream& operator=(const MTcpStream &);
public:
    void send_cb(FnSend send_cb, void *param = 0);
    void recv_cb(FnRecv recv_cb, void *param = 0);

    void update_time(int64_t cur_time);

    int send(const char *buf, int len);
    int recv(const char *buf, int len, int64_t cur_time);
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
    MTcpBuffer _recv_buf;
    uint16_t _send_wnd;
    MTcpBuffer _send_buf;

    int64_t _last_time;
    uint32_t _ts;
    uint32_t _interval;

    MTcpHeader _header;
    std::string _cache;

    FnSend _send_cb;
    void *_send_param;
    FnRecv _recv_cb;
    void *_recv_param;
    int _last_error;
};

#endif
