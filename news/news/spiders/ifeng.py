# -*- coding: utf-8 -*-
import scrapy
import re

from copy import deepcopy

from ..items import NewsItem

class IfengSpider(scrapy.Spider):
    name = 'ifeng'
    allowed_domains = ['ifeng.com']
    start_urls = ['http://search.ifeng.com/sofeng/search.action?q=p2p&c=1&p=1',
                  "http://search.ifeng.com/sofeng/search.action?q=%E7%BD%91%E8%B4%B7&c=1&p=1"]

    def parse(self, response):
        div_list = response.xpath("//div[@class='mainM']/div[@class='searchResults']")

        for div in div_list:
            item = NewsItem()
            item["href"] = div.xpath("./p/a/@href").extract_first()
            if item["href"] is not None:
                yield scrapy.Request(item["href"],callback=self.parse_detail
                                     ,meta={"item":deepcopy(item)})

        key = re.findall(r"action\?q=(.*)&c=1",response.url)[0]
        for i in range(2,11):
            next_url = "http://search.ifeng.com/sofeng/search.action?q={0}&c=1&p={1}".format(key,i)
            yield scrapy.Request(next_url,callback=self.parse)


    def parse_detail(self,response):

        item = deepcopy(response.meta["item"])
        item["title"] = response.xpath("//div[@class='yc_tit']/h1/text()").extract_first()
        # if item["title"] is None:
        #     item["title"] = response.xpath("//div[@id='artical']/h1/text()").extract_first()

        item["update_time"] = response.xpath(
            "//div[@class='yc_tit']/p[@class='clearfix']//span/text()").extract_first()
        item["platform"] = "凤凰新闻"

        content = response.xpath("//div[@class='yc_con_txt']//p/text()").extract()
        if content is not None and len(content) > 0:
            item["content"] = "".join(("".join(content)).split())

        if item["title"] is None:
            item["title"] = response.xpath("//div[@id='artical']/h1/text()").extract_first()
            item["update_time"] = response.xpath(
                "//div[@id='artical_sth']/p[@class='p_time']/span[1]/text()").extract_first()
            content = response.xpath("//div[@id='main_content']//p/text()").extract()
            item["content"] = "".join(("".join(content)).split())
            item["platform"] = "凤凰新闻"

        yield item

        # print(item)


