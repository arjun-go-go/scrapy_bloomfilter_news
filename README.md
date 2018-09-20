# scrapy_bloomfiter_news
scrapy对接bloomfilter，scrapy-deltafetch实现增量爬取

bloomfilter安装pip install pybloom_live

tool下创建BloomCheck.py


#scrapy-deltafetch实现增量爬取

scrapy-deltafetch通过Berkeley DB来记录爬虫每次爬取收集的request和item，当重复执行爬虫时只爬取新的item，实现增量去重，提高爬虫爬取性能。

安装Berkeley DB

安装bsddb3
pip  install  bsddb3

安装scrapy-deltafetch
pip install scrapy-deltafetch

安装scrapy-magicfields

pip install scrapy-magicfields

如果想重新爬取之前已经爬取过的链接，可以通过重置DeltaFetch的缓存来实现，具体做法是给你的爬虫传一个参数deltafetch_reset

scrapy crawl baidu -a deltafetch_reset=1
