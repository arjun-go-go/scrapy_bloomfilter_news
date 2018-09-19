# -*- coding: utf-8 -*-
import re
import scrapy
from copy import deepcopy
from ..items import NewsItem


class CrnttSpider(scrapy.Spider):
    name = 'crntt'
    allowed_domains = ['crntt.com']
    start_urls = ['http://www.crntt.com/crn-webapp/kindOutline.jsp?page=1&Submit=go&coluid=10&kindid=253']

    def parse(self, response):
        li_list = response.xpath("//tr/td/ul/li")
        for li in li_list:
            item = NewsItem()
            item["platform"] = "中评网"
            item["title"] = li.xpath("./a/text()").extract_first()
            item["title"] = "".join(item["title"].split())
            item["update_time"] = li.xpath("./font/em/text()").extract_first()
            if item["update_time"] is not None:
                item["update_time"] = re.findall(r"\((.*)\)", item["update_time"])[0]

            url_info = li.xpath("./a/@href").extract_first()
            if url_info is not None:
                num = re.match(r"/doc/10_253_(.*)_1_(.*)\.html", url_info).group(1)
                item["href"] = "http://www.crntt.com/doc/{0}/{1}/{2}/{3}/{4}.html"\
                    .format(num[:4], num[4], num[5], num[6], num)
                yield scrapy.Request(item["href"], callback=self.parse_detail
                                     , meta={"item": deepcopy(item)})

        for i in range(1, 51):
            next_url = "http://www.crntt.com/crn-webapp/kindOutline.jsp?coluid=10&kindid=253&page={0}".format(i)
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_detail(self,response):
        item = deepcopy(response.meta["item"])
        content = response.xpath("//tr/td[@id='zoom']/text()").extract()
        if content is not None and len(content) > 0:
            item["content"] = "".join(("".join(content)).split())
            # print(item)
            yield item

