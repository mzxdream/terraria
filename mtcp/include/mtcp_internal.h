#ifndef _MTCP_INTERNAL_H_
#define _MTCP_INTERNAL_H_

#include <cstddef>
#include <cstdint>
#include <type_traits>
#include <algorithm>
#include <cstring>

static union { uint8_t a[4]; uint32_t b; } endian_test = {{0, 0, 0, 1}};
#define M_BIG_ENDIAN ((uint8_t)endian_test.b)

template <typename T>
static inline T reverse_any(T val)
{
    uint8_t *data = reinterpret_cast<uint8_t*>(&val);
    std::size_t size = sizeof(val);
    for (std::size_t i = 0; i < size / 2; ++i)
    {
        std::swap(data[i], data[size - 1 - i]);
    }
    return val;
}

template <typename T>
static inline T hton_any(T val)
{
#ifndef M_BIG_ENDIAN
    return reverse_any(val);
#endif
    return val;
}

template <typename T>
static inline T ntoh_any(T val)
{
#ifndef M_BIG_ENDIAN
    return reverse_any(val);
#endif
    return val;
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static bool before(T a, T b)
{
    return static_cast<typename std::make_signed<T>::type>(a - b) < 0;
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static bool before_eq(T a, T b)
{
    return static_cast<typename std::make_signed<T>::type>(a - b) <= 0;
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static bool after(T a, T b)
{
    return static_cast<typename std::make_signed<T>::type>(a - b) > 0;
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static bool after_eq(T a, T b)
{
    return static_cast<typename std::make_signed<T>::type>(a - b) >= 0;
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static typename std::make_signed<T>::type diff(T a, T b)
{
    return static_cast<typename std::make_signed<T>::type>(a - b);
}

template <typename T>
char* encode_any(char *p, T a)
{
    a = hton_any(a);
    memcpy(p, reinterpret_cast<const char*>(&a), sizeof(a));
    return p + sizeof(a);
}

template <typename T>
const char* decode_any(const char *p, T &a)
{
    memcpy(reinterpret_cast<char*>(&a), p, sizeof(a));
    a = hton_any(a);
    return p + sizeof(a);
}

#endif
