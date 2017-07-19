#!/usr/bin/env python
# coding: utf-8

class KcpSegment:
    def __init__(self):
        self._cmd = 0
        self._wnd = 0
        self._ts = 0
        self._sn = 0
        self._una = 0
        self._resendts = 0
        self._rto = 0
        self._fastack = 0
        self._data = bytes()


