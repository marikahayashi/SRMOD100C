#!/usr/bin/env python
# -*- coding:utf-8 -*-
import serial
import time
import binascii

class SRMOD100CClass():
    def __init__(self, devname="/dev/ttyUSB0", baudrate=9600):
        self.devname = devname
        #ボードの認識語句セットが変わった場合はここを編集すること
        self.phrase_table = (
            (),
            ("アクション", "進め", "曲がれ", "走れ", "見ろ", "攻撃", "止まれ", "こんにちは"),
            ("左", "右", "上", "下", "前", "後ろ"),
            ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"),
            (),
            ("助けて", "いってきます", "ただいま", "誰か", "おーい", "こんにちは", "痛い", "こっちに来て"))
        self.seri = serial.Serial(self.devname, baudrate, timeout=0.1)
        self.ntimeout = 10
        self.wordset = 5

    #日本語に言語を設定する
    def set_language(self):
        while 1:
            self.seri.write("\x6c\x43")
            res = self.seri.read()
            if (res == "\x6f"):
                return 0;
        
    def recognize(self, wordset=5):
        self.wordset = wordset
        self.seri.write("\x69")
        self.seri.write(self.convert_number_txchar(self.wordset))
        print "speak"
        time.sleep(2)
        recogres = -1
        ncnt = 0
        while 1:
            ret = self.seri.read()
            if (ret == "\x74"):
                print "timeout"
                break
            elif (ret == "\x65"):
                print "unknown phrase"
                break
            elif (ret == "\x73"):
                self.seri.write("\x20")
                recogres = self.seri.read()
                break
            else:
                ncnt += 1
                if (ncnt > self.ntimeout):
                    print "no response"
                    break
        return recogres

    def convert_number_txchar(self, num):
        return binascii.a2b_hex(b"%x" % (num+0x41))

    def convert_rxchar_number(self, rxchar):
        str = binascii.b2a_hex(rxchar)
        return int(str, 16) - 0x41

    def convert_recogres_japanese(self, recogres):
        return self.phrase_table[self.wordset][self.convert_rxchar_number(recogres)]

    def close():
        self.seri.close()
    
if __name__ == "__main__":
    srmod100c = SRMOD100CClass("/dev/ttyUSB0")
    srmod100c.set_language()
    while 1:
        recogres = srmod100c.recognize(5)
        print recogres
        if (recogres > 0):
            print srmod100c.convert_recogres_japanese(recogres)
        
