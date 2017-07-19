#!/usr/bin/env python
# coding: utf-8

class const(object):
    class ConstError(TypeError):
        pass
    class ConstCaseError(ConstError):
        pass
    def __setter__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "not allowed change const.%s" % value
        if not name.isupper():
            raise self.ConstCaseError, "const.%s is not all uppercase" % name
        self.__dict__[name] = value

import sys
sys.modules[__name__] = const()
