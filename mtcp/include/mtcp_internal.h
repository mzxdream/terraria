#ifndef _MTCP_INTERNAL_H_
#define _MTCP_INTERNAL_H_

#include <cstddef>
#include <cstdint>
#include <type_traits>
#include <algorithm>
#include <cstring>

static const union { uint8_t a[4]; uint32_t b; } endian_test = {{'l', '?', '?', 'b'}};
#define MTCP_ENDIANNESS ((uint8_t)endian_test.b)
#if MTCP_ENDIANNESS == 'l'
    #define MTCP_LITTLE_ENDIAN
#elif
    #define MTCP_BIG_ENDIAN
#endif

template <typename T>
static inline T mtcp_hton(T val)
{
#ifdef MTCP_LITTLE_ENDIAN
    uint8_t *data = reinterpret_cast<uint8_t*>(&val);
    std::size_t size = sizeof(val);
    for (std::size_t i = 0; i < size / 2; ++i)
    {
        std::swap(data[i], data[size - 1 - i]);
    }
#endif
    return val;
}
#define mtcp_ntoh mtcp_hton

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static typename std::make_signed<T>::type mtcp_diff(T a, T b)
{
    return static_cast<typename std::make_signed<T>::type>(a - b);
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static bool mtcp_before(T a, T b)
{
    return static_cast<typename std::make_signed<T>::type>(a - b) < 0;
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static bool mtcp_before_eq(T a, T b)
{
    return static_cast<typename std::make_signed<T>::type>(a - b) <= 0;
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static bool mtcp_after(T a, T b)
{
    return static_cast<typename std::make_signed<T>::type>(a - b) > 0;
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static bool mtcp_after_eq(T a, T b)
{
    return static_cast<typename std::make_signed<T>::type>(a - b) >= 0;
}

typedef struct
{
    uint32_t seq;
    uint32_t ack_seq;
    uint32_t ts;
    uint32_t ack_ts;
    uint16_t cmd;
    uint16_t window;
    std::list<uint32_t> _sack_list;
}MTcpHeader;

#endif
