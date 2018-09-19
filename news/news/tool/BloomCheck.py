# -*- coding: utf-8 -*-
# author: Arjun
# @Time: 18-7-10 下午4:09


from pybloom_live import BloomFilter
import os
import hashlib

class BloomCheckFunction(object):
    def __init__(self):
        self.filename = 'bloomFilter.blm'
        is_exist = os.path.exists(self.filename)
        if is_exist:
            self.bf = BloomFilter.fromfile(open(self.filename, 'rb'))
        else:
            self.bf = BloomFilter(100000000, 0.001)
    def process_item(self, data):
        data_encode_md5 = hashlib.md5(data.encode(encoding='utf-8')).hexdigest()
        if data_encode_md5 in self.bf:
            return False
        else:
            self.bf.add(data_encode_md5)
            return True

    def save_bloom_file(self):
        self.bf.tofile(open(self.filename, 'wb'))