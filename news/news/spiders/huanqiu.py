# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from ..items import NewsItem


class HuanqiuSpider(scrapy.Spider):
    name = 'huanqiu'
    allowed_domains = ['huanqiu.com']
    start_urls = ["http://finance.huanqiu.com/jinr/index.html",
                  "http://finance.huanqiu.com/baoxianl/index.html"
                ]

    def parse(self, response):
        li_list = response.xpath("//div[@class='fallsFlow']/ul/li")
        for li in li_list:
            item = NewsItem()
            item["title"] = li.xpath("./h3/a/@title").extract_first()
            item["href"] = li.xpath("./h3/a/@href").extract_first()
            if item["href"] is not None:
                yield scrapy.Request(item["href"], callback=self.parse_detail
                                     , meta={"item": deepcopy(item)})

        next_url = response.xpath(
            "//div[@id='pages']/a[contains(text(),'下一页')]/@href").extract_first()
        if next_url is not None:
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_detail(self,response):

        item = deepcopy(response.meta["item"])
        update_time_1 = response.xpath(
            "//div[@class='la_tool']/span[1]/text()").extract_first()
        platform_1 = response.xpath(
            "//div[@class='la_tool']/span[2]/a/text()").extract_first()

        update_time_2 = response.xpath(
            "//div[@class='summaryNew']/strong[1]/text()").extract_first()
        platform_2 = response.xpath(
            "//div[@class='summaryNew']/strong[2]/a/text()").extract_first()
        content_1 = response.xpath("//div[@class='la_con']//p/text()").extract()
        content_2 = response.xpath("//div[@class='text']//p/text()").extract()

        if update_time_1 is not None:
            item["update_time"] = update_time_1
            item["platform"] = platform_1
            item["content"] = "".join(("".join(content_1)).split())
            # print(item)
            yield item
        else:
            item["update_time"] = update_time_2
            item["content"] = "".join(("".join(content_2)).split())
            item["platform"] = platform_2
            # print(item)
            yield item
        # yield item