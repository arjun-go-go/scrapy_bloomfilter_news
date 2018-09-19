# -*- coding: utf-8 -*-
# author: arjun
# @Time: 18-4-25 上午10:36

import pymysql
conn = pymysql.connect('47.96.94.94', 'admin', 's@11##!4', 'p2p2', charset="utf8")
cursor = conn.cursor()
def seach_sql_all():
    # 1.查询操作
    # 编写sql 查询语句  user 对应我的表名
    try:
        sql = """select net_name from tp_com_info"""
        cursor.execute(sql)
        results = cursor.fetchall()
        name_list = []
        for i in results:
            name_list.append(i[0])
        return name_list
    except Exception as e:
        print(e)

if __name__ == '__main__':
  pass



