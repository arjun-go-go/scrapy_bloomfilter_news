# -*- coding: utf-8 -*-
# author: arjun
# @Time: 18-5-10 下午2:18


import datetime
def handle_time():
    start = '20170501'
    end = '20180510'
    datestart = datetime.datetime.strptime(start, '%Y%m%d')
    dateend = datetime.datetime.strptime(end, '%Y%m%d')
    while datestart < dateend:
        datestart += datetime.timedelta(days=1)
        # print(datestart.strftime('%Y%m%d'))
        return datestart.strftime('%Y%m%d')

# print(handle_time())

