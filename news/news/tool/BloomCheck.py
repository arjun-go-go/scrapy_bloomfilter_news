# -*- coding: utf-8 -*-
# author: Arjun
# @Time: 18-6-10 下午4:09


from pybloom_live import BloomFilter
import os
import hashlib
class BloomCheckFunction(object):
    def __init__(self):
        self.filename = 'bloomFilter.blm'
        # 判断文件是否存在
        is_exist = os.path.exists(self.filename)
        # 存在直接打开 储存在内存中
        if is_exist:
            self.bf = BloomFilter.fromfile(open(self.filename, 'rb'))
        else:
            # 新建一个 储存在内存中
            self.bf = BloomFilter(100000000, 0.001)
    def process_item(self, data):
        data_encode_md5 = hashlib.md5(data.encode(encoding='utf-8')).hexdigest()
        # 内容没有更新 丢弃item return False
        if data_encode_md5 in self.bf:
            return False
        else:
            # 内容不存在，新来的 return True
            self.bf.add(data_encode_md5)
            return True
    def save_bloom_file(self):
        self.bf.tofile(open(self.filename, 'wb'))
