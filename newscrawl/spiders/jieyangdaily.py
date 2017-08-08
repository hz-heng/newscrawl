# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class JieYangDailySpider(scrapy.Spider):
    name = "jieyangdaily"
    allowed_domains = ["jieyangdaily.com"]
    base_url = "http://www.jyrb.net.cn/"
    newspapers = "揭阳日报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y%m%d')
        url = self.base_url + 'news/index%s.html' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        articles = response.xpath('//map/area/@href').extract()
        #当前页面没数据则重爬
        if response.status == 404 or  not articles:
            time.sleep(1800) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for article in articles:
            article_path = re.findall('(?<=../).*', article)[0]
            url = self.base_url + article_path
            #yield Request(url, self.article_parse)

    def article_parse(self, response):
        list_title = response.xpath('//td[@class="jyrb05"]/text()').extract()
        title = "".join(list_title).strip()
        list_content = response.xpath('//td[@class="jyrb07"]/p/text()').extract()
        content = "".join(list_content).strip()
        list_date = re.findall('(?<=/)\d{1,}(?=/)', response.url)
        str_date = "".join(list_date)
        date = str_date[:4] + '-' + str_date[4:6] + '-' + str_date[6:8]
        page = 'null'
        category = 'null'
        if content == "":
            pass
        else:
            item = newsItem()
            item['title'] = title
            item['page'] = page
            item['content'] = content
            item['date'] = date
            item['category'] = category
            item['url'] = response.url
            item['newspapers'] = self.newspapers
            yield item
