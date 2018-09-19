# -*- coding: utf-8 -*-
# author: Arjun
# @Time: 18-6-22 下午1:47
import time
import re
#
# def datestamptrans(date):
#     timelist = re.split(r'[^0-9]', date)
#     print(timelist)
#     if len(timelist[0]) == 4:
#         year = timelist[0]
#         month = timelist[1] if len(timelist[1])==2 else '0' + timelist[1]
#         day = timelist[2] if len(timelist[2])==2 else '0' + timelist[1]
#         return int(time.mktime(time.strptime(year + '-' + month + '-' + day, "%Y-%m-%d")))
#     elif len(timelist[0]) == 2:
#         year = 2018
#         month = timelist[1] if len(timelist[0])==2 else '0' + timelist[1]
#         day = timelist[2] if len(timelist[1])==2 else '0' + timelist[1]
#         return int(time.mktime(time.strptime(year+'-'+month+'-'+day, "%Y-%m-%d")))


def datestamptrans(date_time):
    year = ""
    month = ""
    day = ""
    str_date = str(date_time)
    timelist = re.split(r'[^0-9]', str_date)
    if len(timelist[0]) == 4:
        year = timelist[0]
        month = timelist[1] if len(timelist[1]) == 2 else '0' + timelist[1]
        day = timelist[2] if len(timelist[2]) == 2 else '0' + timelist[1]
    elif len(timelist[0]) == 2:
        year = 2018
        month = timelist[0] if len(timelist[0])==2 else '0' + timelist[1]
        day = timelist[1] if len(timelist[1])==2 else '0' + timelist[1]
    return int(time.mktime(time.strptime(str(year)+'-'+str(month)+'-'+str(day), "%Y-%m-%d")))


if __name__ == '__main__':
    dd = datestamptrans("2018-06-22")
    print(dd)
