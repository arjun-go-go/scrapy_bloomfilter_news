# -*- coding: utf-8 -*-

# Define your item pipelines here
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from twisted.enterprise import adbapi
from news.tool.BloomCheck import BloomCheckFunction


class NewsPipeline(object):
    def process_item(self, item, spider):
        return item


class DynamicMysqlPipeline(object):
    #采用同步的机制写入mysql
    def __init__(self):
        self.conn = pymysql.connect('172.16.20.216', 'root', 'mysql', 'wangdai', charset="utf8")
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):

        data = {
            "title":item["title"],
            "content":item["content"],
            "update_time":item["update_time"]
        }
        table = "news"

        keys = ",".join(data.keys())
        values = ",".join(['%s']*len(data))

        insert_sql = """
            insert into {table}({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE """\
            .format(table=table,keys=keys,values=values)

        update = ",".join(["{key}= %s".format(key=key) for key in data])
        insert_sql += update
        try:
            if self.cursor.execute(insert_sql, tuple(data.values())*2):
                print("successful")
                self.conn.commit()

        except Exception as e:
            print("Failed")
            self.conn.rollback()



class MysqlTwistedPipline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider) #处理异常

    def handle_error(self, failure, item, spider):
        #处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # if self.bof.process_item(item["title"]):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)

