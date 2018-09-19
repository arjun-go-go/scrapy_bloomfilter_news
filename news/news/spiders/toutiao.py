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


class ToutiaoSpider(scrapy.Spider):
    name = 'toutiao'
    allowed_domains = ['toutiao.com']
    start_urls = [
        'https://www.toutiao.com/search_content/?offset={0}&format=json&keyword={1}&autoload=true&count=20&cur_tab=1&from=search_tab']
    search_field = ['p2p', '理财', '网贷']

    def __init__(self):
        self.bof = BloomCheckFunction()
        super(ToutiaoSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        print("*" * 50)
        print("spider closed")
        self.bof.save_bloom_file()

    def start_requests(self):
        for i in range(0, 2):
            for search in self.search_field:
                yield scrapy.Request(
                    self.start_urls[0].format(i * 20, search),
                    callback=self.parse,
                )

    def parse(self, response):
        result = json.loads(response.body.decode())
        revs = result['data']
        for rev in revs:
            item = NewsItem()
            item["update_date"] = str(datetime.date.today())
            try:
                item['title'] = rev['title']
            except:
                pass
            # item['postive_score'] = handle_tag(item['title'])
            item['postive_score'] = 0
            try:
                item['update_time'] = rev['datetime']
                if item['update_time'] is not None:
                    item['news_time'] = datestamptrans(item['update_time'])
            except:
                pass
            item['platform'] = "今日头条"
            try:
                if item['title'] and self.bof.process_item(item["title"]):
                    detail_url = rev['source_url']
                    item['href'] = "https://www.toutiao.com" + detail_url
                    yield scrapy.Request(
                        item['href'],
                        callback=self.detail_parse,
                        meta={"item": deepcopy(item)})
            except:
                pass

    def detail_parse(self, response):
        item = deepcopy(response.meta["item"])
        content_list = re.findall(r"content:\s?'(.+?)',\s+", response.body.decode())
        if len(content_list) > 0:
            item['content'] = ''.join(''.join(re.sub(r"&lt;.+?&gt;", '', content_list[0])).split())
            yield item
