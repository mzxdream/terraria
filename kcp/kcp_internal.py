#!/usr/bin/env python
# coding: utf-8

from . import const

const.KCP_RTO_NDL = 30
const.KCP_RTO_MIN = 100
const.KCP_RTO_DEF = 200
const.KCP_RTO_MAX = 60000

const.KCP_CMD_PUSH = 81
const.KCP_CMD_ACK = 82
const.KCP_CMD_WASK = 83
const.KCP_CMD_WINS = 84

const.KCP_ASK_SEND = 1
const.KCP_ASK_TELL = 2

const.KCP_WND_SND = 32
const.KCP_WND_RCV = 32

const.KCP_MTU_DEF = 1400

const.KCP_ACK_FASK = 3

const.KCP_INTERVAL = 100

const.KCP_OVERHEAD = 24

const.KCP_DEADLINK = 20

const.KCP_THRESH_INIT = 2
const.KCP_THRESH_MIN = 2

const.KCP_PROBE_INIT = 7000
const.KCP_PROBE_LIMIT = 120000

def u32_next(a):
    return (a + 1) & 0xFFFFFFFF

def u32_diff(a, b):
    diff = a - b
    if diff > 0x7FFFFFFF:
        return diff - 0xFFFFFFFF
    if diff < -0x7FFFFFFF:
        return diff + 0xFFFFFFFF
    return diff



