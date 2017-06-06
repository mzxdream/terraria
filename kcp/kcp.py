#!/usr/bin/env python
# coding: utf-8

def next_seq(seq):
    if seq >= 0xFFFFFFFF:
        return 0
    return seq + 1

def before_seq(seq1, seq2):
    result = seq1 - seq2
    if result < 0:
        return result >= -0x7FFFFFFF
    else:
        return result > 0x7FFFFFFF

def before_eq_seq(seq1, seq2):
    result = seq1 -seq2
    if result <= 0:
        return result >= -0x7FFFFFFF
    else:
        return result > 0x7FFFFFFF

def after_seq(seq1, seq2):
    result = seq1 - seq2
    if result <= 0:
        return result < -0x7FFFFFFF
    else:
        return result <= 0x7FFFFFFF

def after_eq_seq(seq1, seq2):
    result = seq1 - seq2
    if result < 0:
        return result < -0x7FFFFFFF
    else:
        return result <= 0x7FFFFFFF

class Kcp:
    def __init__(self):
        pass

if __name__ == "__main__":
    while True:
        test = raw_input("xxxxxxx").split(" ")
        if len(test) != 2:
            print("input error")
            continue
        seq1 = int(test[0])
        seq2 = int(test[1])
        print("befor_seq:", before_seq(seq1, seq2))
        print("befor eq seq:", before_eq_seq(seq1, seq2))
        print("after_seq:", after_seq(seq1, seq2))
        print("after_eq_seq:", after_eq_seq(seq1, seq2))

