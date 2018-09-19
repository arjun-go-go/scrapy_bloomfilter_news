# -*- coding: utf-8 -*-
import scrapy
import re
from copy import deepcopy

from ..items import NewsItem


class CnfolSpider(scrapy.Spider):
    name = 'cnfol'
    allowed_domains = ['cnfol.com']
    start_urls = ["http://so.cnfol.com/cse/search?q=p2p&p=0&s=12596448179979580087",
                  "http://so.cnfol.com/cse/search?q=%E7%BD%91%E8%B4%B7&p=0&s=12596448179979580087"]

    def parse(self, response):
        div_list = response.xpath("//div[@id='results']/div")

        for div in div_list:
            item = NewsItem()
            item["href"] = div.xpath("./h3/a/@href").extract_first()
            if item["href"] is not None:
                yield scrapy.Request(item["href"],callback=self.parse_detail
                                     ,meta={"item":deepcopy(item)})
        url_info = response.xpath(
                "//div[@id='pageFooter']/a[contains(text(),'下一页')]/@href").extract_first()
        if url_info is not None:
            next_url = "http://so.cnfol.com/cse/" + url_info
            yield scrapy.Request(next_url,callback=self.parse)


    def parse_detail(self,response):

        item = response.meta["item"]
        if "2018" in item["href"]:
            item["title"] = response.xpath(
                "//div[@class='artMain mBlock']/h3[@class='artTitle']/text()").extract_first()

            item["update_time"] = response.xpath(
                "//div[@class='artDes']/span[1]/text()").extract_first()
            platform = response.xpath(
                "//div[@class='artDes']/span[2]/text()").extract_first()
            if platform is not None:
                item["platform"] = re.findall(r"来源:(.*)", platform)[0]

            content = response.xpath("//div[@class='Article']//text()").extract()
            if content is not None and len(content) > 0:
                item["content"] = "".join(("".join(content)).split())
                # print(item)
                yield item

        else:
            item["title"] = response.xpath(
                    "//div[@class='Art NewArt']/h1/text()").extract_first()
            item["update_time"] = response.xpath(
                    "//span[@id='pubtime_baidu']/text()").extract_first()
            item["platform"] = response.xpath(
                "//span[@id='source_baidu']/span/text()").extract_first()
            if item["platform"] is None:
                item["platform"] = response.xpath(
                    "//span[@id='source_baidu']/a/text()").extract_first()
            content = response.xpath("//div[@id='Content']//text()").extract()
            if content is not None and len(content) > 0:
                item["content"] = "".join(("".join(content)).split())
                # print(item)
                yield item