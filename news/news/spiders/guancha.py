# -*- coding: utf-8 -*-
import re
import scrapy
from copy import deepcopy
from ..items import NewsItem


class GuanchaSpider(scrapy.Spider):
    name = 'guancha'
    allowed_domains = ['guancha.cn']
    start_urls = ['http://www.guancha.cn/Search/?k=P2P',
                  "http://www.guancha.cn/Search/?k=%E7%BD%91%E8%B4%B7"]

    def parse(self, response):

        dd_list = response.xpath("//dl[@class='search-list']/dd")
        for dd in dd_list:
            item = NewsItem()
            item["title"] = dd.xpath("./h4/a/text()").extract_first()
            item["href"] = dd.xpath("./h4/a/@href").extract_first()
            if item["href"] is not None:
                item["href"] = "http://www.guancha.cn" + item["href"]
                yield scrapy.Request(item["href"], callback=self.parse_detail
                                     , meta={"item": deepcopy(item)})

        url_info = response.xpath(
            "//div[@id='Pagination']/a[contains(text(),'下一页')]/@href").extract_first()
        if url_info is not None:
            next_url = "http://www.guancha.cn/Search/" + url_info
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_detail(self,response):

        item = deepcopy(response.meta["item"])
        item["update_time"] = response.xpath("//div[@class='time fix']/span[1]/text()").extract_first()
        # if item["update_time"] is not None:
        #     item["update_time"] = "".join(item["update_time"].split())
        platform = response.xpath("//div[@class='time fix']/span[3]/text()").extract_first()
        if platform is not None:
            item["platform"] = re.findall(r"来源：(.*)", platform)[0]
            # print(item["platform"])
        content = response.xpath("//div[@class='content all-txt']//p/text()").extract()
        if content is not None and len(content) > 0:
            item["content"] = "".join(("".join(content)).split())

            yield item
            # print(item)



