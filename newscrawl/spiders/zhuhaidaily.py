# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class ZhuHaiDailySpider(scrapy.Spider):
    name = "zhuhaidaily"
    allowed_domains = ["zhuhaidaily.com.cn"]
    base_url = "http://zhuhaidaily.com.cn/"
    newspapers = "珠海特区报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y-%m-%d')
        url = self.base_url + 'list.php?ud_date=%s' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        articles = response.xpath('//*[@id="main"]/ul/li/a/@href').extract()
        #当前页面没数据则重爬
        if response.status == 404 or not articles:
            time.sleep(18) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for article in articles:
            url = self.base_url + article
            yield Request(url, self.article_parse)

    def article_parse(self, response):
        list_title = response.xpath('//div[@id="main"]/h1/text()').extract()
        title = "".join(list_title)
        list_content = response.xpath('//div[@id="main"]/p/text()').extract()
        content = "".join(list_content)
        date = re.findall('\d{1,}-\d{1,}-\d{1,}', response.url)[0]
        list_page = response.xpath('//div[@id="main"]/div/ul/li[1]/a/text()').extract()
        str_page = "".join(list_page)
        page = re.findall('\w{1,}', str_page, re.A)[0]
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
