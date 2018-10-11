# -*- coding:utf-8 -*-
# Author : kjy
# Date : 18. 9. 27
# Version : v1.0
# Explanation : 공유 라이브러리

import hashlib
import struct


def md5(data):
    return hashlib.md5(data).hexdigest()


def get_uint16(buf, off):
    return struct.unpack('<H', buf[off:off+2])[0]


def get_uint32(buf, off):
    return struct.unpack('<L', buf[off:off+4])[0]

def vprint(header, section=None, msg=None):
    if header:
        print '[*] %s' % header

    if section:
        if len(msg) > 50:
            new_msg = msg[:22] + ' ... ' + msg[-22:]
        else:
            new_msg = msg
        print '    [-] %-20s: %s' % (section, new_msg)

class LVModule:
    def init(self, modulePath):
        return 0

    def uninit(self):
        return 0

    def getInfo(self):
        info = dict()

        info['author'] = 'kjy'
        info['version'] = '1.0'
        info['title'] = 'Share Libary'
        info['moduleName'] = 'sharelib'

        return info
