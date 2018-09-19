# -*- coding: utf-8 -*-
import datetime
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


class BaiduSpider(scrapy.Spider):
    name = 'baidu'
    allowed_domains = ['baidu.com', 'baiducontent.com']
    start_urls = ['http://news.baidu.com/ns?word=%28%20%22%E5%B0%8F%E4%B9%9D%E9%87%91%E6%9C%8D%22%20%29&pn=0&cl=2&ct=1&tn=news&rn=20&ie=utf-8&bt=0&et=0&rsv_page=1']

    def __init__(self):
        self.bof = BloomCheckFunction()
        super(BaiduSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        print("*"*50)
        print("spider closed")
        self.bof.save_bloom_file()


    def start_requests(self):
        name_list = seach_sql_all()
        # name_list = []
        for name in name_list:
            url = 'http://news.baidu.com/ns?word=(%20"{}"%20)&pn=0' \
                  '&cl=2&ct=1&tn=news&rn=20&ie=utf-8&bt=0&et=0&rsv_page=1'.format(name)
            yield scrapy.Request(url,callback=self.parse)

    def parse(self, response):
        item = NewsItem()
        div_list = response.xpath("//div[@class='result']")
        for div in div_list:
            item["update_date"] = str(datetime.date.today())
            try:
                name_info = re.findall(r"http:\/\/news\.baidu\.com\/ns\?word=\(%20%22(.*)%22%20\)&pn=.*", response.url)[0]
            except Exception as e:
                name_info = re.match(r"http:\/\/news\.baidu\.com\/ns\?word=%28%20%22(.*)%22%20%29&pn=.*",response.url).group(1)

            text = unquote(name_info, "utf-8")
            title_list = div.xpath("./h3/a/text()|./h3/a/em/text()").extract()
            if len(title_list) > 0:
                title = ''.join(''.join(title_list).split())
                if title is not None and title.__contains__(text):
                    item['title'] = title
                    item["postive_score"] = None
            # 发布信息
            public_str = div.xpath(".//p[@class='c-author']/text()").extract_first()
            if public_str is not None:
                update_time = ''.join(public_str).split()
                if len(update_time) >= 3:
                    item['update_time'] = update_time[1]+update_time[2]
                    item['news_time'] = datestamptrans(item['update_time'])
                    item['platform'] = update_time[0]
                else:
                    item['update_time'] = update_time[0] + update_time[1]
                    item['news_time'] = datestamptrans(item['update_time'])
                    item['platform'] = "百度新闻"
            try:
                if item['title'] and self.bof.process_item(item["title"]):
                    detail_url = div.xpath(".//a[@class='c-cache']/@href").extract_first()
                    if detail_url is not None:
                        url_con = re.match(r"http:\/\/cache\.baidu\.com\/c\?m=(.*)",detail_url).group(1)
                        item['href'] = "http://cache.baiducontent.com/c?m=" + url_con
                        yield scrapy.Request(
                            item['href'],
                            callback=self.detail_parse,
                            meta={'item': deepcopy(item)}
                            )
            except Exception as e:
                pass

        next_url = response.xpath("//a[contains(text(),'下一页')]/@href").extract_first()
        if next_url is not None:
            page_num = re.search(r'pn=(\d+)', next_url).group(1)
            if int(page_num) <= 20:
                next_url = "http://news.baidu.com" + next_url
                yield scrapy.Request(
                    next_url,
                    callback=self.parse)
        #
        # for div in div_list:
        #     # 数据更新时间
        #     item["update_date"] = str(datetime.date.today())
        #     item["postive_score"] = None
        #     # 新闻标题
        #     item['title'] = div.xpath("./h3/a/text()|./h3/a/em/text()").extract()
        #     item['title'] = ''.join(''.join(item['title']).split())
        #     if item['title'] is not None and item['title'].__contains__("小九金服"):
        #         item['title'] = item['title']
        #     # 发布信息
        #     public_str = div.xpath(".//p[@class='c-author']/text()").extract_first()
        #     if public_str is not None and len(''.join(public_str).split()) == 3:
        #         # 发布时间
        #         item['update_time'] = ''.join(public_str).split()[1] + ''.join(public_str).split()[2]
        #         # 新闻来源
        #         item['platform'] = ''.join(public_str).split()[0]
        #     elif public_str is not None and len(''.join(public_str).split()) == 2:
        #         item['update_time'] = ''.join(public_str).split()[0] + ''.join(public_str).split()[1]
        #         # 新闻来源
        #         item['platform'] = '百度新闻'
        #     else:
        #         item['update_time'] = str(datetime.date.today())
        #         # 新闻来源
        #         item['platform'] = '百度新闻'
        #     if item['update_time'] is not None:
        #         # 新闻发布时间戳
        #         item['news_time'] = datestamptrans(item['update_time'])
        #     # 正文内容对应url
        #     item['href'] = div.xpath("./h3/a/@href").extract_first()
        #     # 百度快照url
        #     detail_url = div.xpath(".//a[@class='c-cache']/@href").extract_first()
        #     if detail_url is not None:
        #         yield scrapy.Request(
        #             detail_url,
        #             callback=self.detail_parse,
        #             meta={'item': deepcopy(item)}
        #         )
        #
        # next_url = response.xpath("//a[contains(text(),'下一页')]/@href").extract_first()
        # if next_url is not None:
        #     page_num = re.search(r'pn=(\d+)', next_url).group(1)
        #     if int(page_num) <= 20:
        #         next_url = "http://news.baidu.com" + next_url
        #         yield scrapy.Request(
        #             next_url,
        #             callback=self.parse)

    def detail_parse(self, response):
        item = deepcopy(response.meta["item"])
        content = response.xpath(
            "//p[position()>1]/text()|//p[position()>1]/font/text()|//p[position()>1]/strong/text()").extract()
        if content is not None and len(content) > 0:
            item['content'] = ''.join(''.join(content).split())
            # print(item)
            yield item
