# -*- coding: utf-8 -*-
import datetime
import datetime
import scrapy
from copy import deepcopy
from ..items import NewsItem

class StockstarSpider(scrapy.Spider):
    name = 'stockstar'
    allowed_domains = ['stockstar.com']
    start_urls = ['http://stockstar.com/']

    def start_requests(self):
        nowTime = datetime.datetime.now().strftime('%Y%m%d')
        start = '20170528'
        end = nowTime
        datestart = datetime.datetime.strptime(start, '%Y%m%d')
        dateend = datetime.datetime.strptime(end, '%Y%m%d')
        while datestart < dateend:
            datestart += datetime.timedelta(days=1)
            t = datestart.strftime('%Y%m%d')
            url = "http://www.stockstar.com/roll/all_{}.shtml".format(t)
            yield scrapy.Request(url,callback=self.parse)

    def parse(self, response):
        ul_list = response.xpath("//div[@class='content cb']/ul[@class='list-line']")
        for ul in ul_list:
            li_list = ul.xpath("./li")
            for li in li_list:
                item = NewsItem()
                href = li.xpath("./a/@href").extract_first()
                if "shtml" in href:
                    item["href"] = href
                    item["title"] = li.xpath("./a/text()").extract_first()
                    yield scrapy.Request(item["href"],callback=self.parse_detail
                                        ,meta={"item":deepcopy(item)})

        url_info = response.xpath("//div[@id='Page']/span[2]/a/@href").extract_first()
        if url_info is not None:
            next_url = "http://www.stockstar.com/roll/" + url_info
            yield scrapy.Request(next_url,callback=self.parse)

    def parse_detail(self,response):
        item = deepcopy(response.meta["item"])
        item["update_time"] = response.xpath(
            "//div[@class='source']/span[@id='pubtime_baidu']/text()").extract_first()

        item["platform"] = response.xpath(
            "//div[@class='source']//span[@id='source_baidu']/a/text()").extract_first()
        if not item["platform"]:
            item["platform"] = response.xpath(
                "//div[@class='source']//span[@id='source_baidu']//text()").extract_first()

        content = response.xpath("//div[@class='article']//p/text()").extract()
        if content is not None and len(content) > 0:
            item["content"] = "".join(("".join(content)).split())
            yield item
            # print(item)