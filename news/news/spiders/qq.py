# -*- coding: utf-8 -*-
import datetime
import json
import re
from copy import deepcopy
from urllib.parse import unquote
import scrapy
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from news.tool.connet_mysql import seach_sql_all
from news.items import NewsItem
from news.tool.handle import datestamptrans
from news.tool.BloomCheck import BloomCheckFunction


class QqSpider(scrapy.Spider):
    name = 'qq'
    allowed_domains = ['qq.com']
    start_urls = [
        'http://pacaio.match.qq.com/irs/rcd?cid=52&token=8f6b50e1667f130c10f981309e1d8200&ext=3910,3911,3904,3901,3906,3912,3917,3902&page=0']

    def __init__(self):
        self.bof = BloomCheckFunction()
        super(QqSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        print("*"*50)
        print("spider closed")
        self.bof.save_bloom_file()


    def start_requests(self):
        headers = {
            'Referer': 'http://new.qq.com/ch2/licai',
        }
        yield scrapy.Request(
            self.start_urls[0],
            headers=headers,
            callback=self.parse
        )

    def parse(self, response):
        res = json.loads(response.body.decode())
        revs = res["data"]
        for rev in revs:
            item = NewsItem()
            item["update_date"] = str(datetime.date.today())
            item['title'] = rev['title']
            # item['postive_score'] = handle_tag(item['title'])
            item['postive_score'] = 0
            update_time = rev['update_time']
            if update_time is not None:
                item['update_time'] = update_time
                item['news_time'] = datestamptrans(item['update_time'])
            item['platform'] = rev['source']
            item['href'] = rev['vurl']
            a_re = re.search(r'\.html', item['href'])
            if a_re:
                item['href'] = rev['vurl']
            else:
                item['href'] = rev['vurl'][0:-2] + ".html"
            if item['title'] and self.bof.process_item(item["title"]):
                yield scrapy.Request(
                    item['href'],
                    callback=self.detail_parse,
                    meta={"item": deepcopy(item)}
                )

    def detail_parse(self, response):
        item = deepcopy(response.meta["item"])
        content = response.xpath("string(//div[@class='content-article'])").extract()
        if len(content) > 0:
            item['content'] = ''.join(''.join(content).split())
            yield item

