#ifndef _MTCP_INTERNAL_H_
#define _MTCP_INTERNAL_H_

#include <cstddef>
#include <cstdint>
#include <type_traits>

static union { uint8_t a[4]; uint32_t b; } endian_test = {{0, 0, 0, 1}};
#define M_IS_BIG_ENDIAN ((uint8_t)endian_test.b)


template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static bool before(T a, T b) {
    return static_cast<std::make_signed<T>::type>(a - b) < 0;
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static bool before_eq(T a, T b) {
    return static_cast<std::make_signed<T>::type>(a - b) <= 0;
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static bool after(T a, T b) {
    return static_cast<std::make_signed<T>::type>(a - b) > 0;
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static bool after_eq(T a, T b) {
    return static_cast<std::make_signed<T>::type>(a - b) >= 0;
}

template <typename T, typename std::enable_if<std::is_unsigned<T>::value, int>::type = 0>
static T next_power_2(T val) {
    --val;
    for (std::size_t i = 1; i < sizeof(val) * 8; i <<= 1) {
        val |= (val >> i);
    }
    return ++val;
}

#endif
