# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    content = scrapy.Field()
    update_time = scrapy.Field()
    platform = scrapy.Field()
    href = scrapy.Field()
    news_time = scrapy.Field()
    update_date = scrapy.Field()
    postive_score = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                         insert into tp_news (title,content,update_time,platform,url,news_time,update_date,postive_score
                           ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)

                     """
        params = (
            self["title"],self["content"],self["update_time"],self["platform"]
            ,self["href"],self["news_time"],self["update_date"],self["postive_score"]
        )
        return insert_sql, params



