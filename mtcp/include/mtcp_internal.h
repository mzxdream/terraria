#ifndef _MTCP_INTERNAL_H_
#define _MTCP_INTERNAL_H_

#include <cstddef>
#include <cstdint>
#include <type_traits>
#include <algorithm>

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
static T next_power_2(T val)
{
    --val;
    for (std::size_t i = 1; i < sizeof(val) * 8; i <<= 1) {
        val |= (val >> i);
    }
    return ++val;
}

#endif
