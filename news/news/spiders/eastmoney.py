# -*- coding: utf-8 -*-
import re
import scrapy
import json
from copyheaders import headers_raw_to_dict
from copy import deepcopy
from ..items import NewsItem

class EastmoneySpider(scrapy.Spider):
    name = 'eastmoney'
    allowed_domains = ['eastmoney.com']
    start_urls = [
        "http://so.eastmoney.com/Web/GetSearchList?type=20&pageindex=1&pagesize=10&keyword=p2p",
        "http://so.eastmoney.com/Web/GetSearchList?type=20&pageindex=1&pagesize=10&keyword=%E7%BD%91%E8%B4%B7"]

    headers = headers_raw_to_dict(b"""
    Accept: application/json, text/javascript, */*; q=0.01
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: keep-alive
    Cookie: st_pvi=30099927179991; qgqp_b_id=99dcb4ed9289ac2173a60b9a6f64960f; st_si=65633279071907; emshistory=%5B%22p2p%22%2C%22P2P%22%2C%22%E7%BD%91%E8%B4%B7%22%2C%22ddd%22%2C%22ddd%5C%5C%22%2C%22%E4%BA%BA%E4%BC%97%E9%87%91%E6%9C%8D%22%5D
    Host: so.eastmoney.com
    Referer: http://so.eastmoney.com/web/s?keyword=p2p&PageIndex=1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36
    """)

    def start_requests(self):
        for url in self.start_urls:

            yield scrapy.Request(url,headers=self.headers,callback=self.parse)


    def parse(self, response):
        dict_response = json.loads(response.body.decode())
        datas = dict_response["Data"]
        for data in datas:
            item = NewsItem()
            item["title"] = data["Art_Title"].replace("<em>", "") \
                .replace("</em>", "")
            item["href"] = data["Art_Url"]
            yield scrapy.Request(item["href"],callback=self.parse_detail,meta={"item":deepcopy(item)})

        key = re.findall(r"\&keyword\=(.*)",response.url)[0]
        for i in range(2, 351):
            next_url = "http://so.eastmoney.com/Web/GetSearchList?type=20"\
                   "&pageindex={0}&pagesize=10&keyword={1}".format(i, key)
            yield scrapy.Request(next_url,callback=self.parse,headers=self.headers)

    def parse_detail(self,response):

        item = deepcopy(response.meta["item"])
        item["update_time"] = response.xpath(
            "//div[@class='Info']/div[@class='time-source']/div[@class='time']/text()").extract_first()
        item["platform"] = response.xpath(
            "//div[@class='Info']/div[@class='time-source']/span/a/text()").extract_first()
        content = response.xpath("//div[@id='ContentBody']//p/text()").extract()
        if len(content) > 0:
            item["content"] = "".join(("".join(content)).split())
            yield item
            # print(item)

