# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class MaoMingDailySpider(scrapy.Spider):
    name = "maomingdaily"
    allowed_domains = ["mm111.net"]
    base_url = "http://paper.mm111.net"
    newspapers = "茂名日报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y%m%d')
        url = self.base_url + '/shtml/mmrb/%s/' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        pages = response.xpath('//div[@class="pageNav"]/ul/li/a/@href').extract()
        #当前页面没数据则重爬
        if response.status == 404 or  not pages:
            time.sleep(1800) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for page in pages:
            url = self.base_url + page
            yield Request(url, self.page_parse, dont_filter=True)

    def page_parse(self, response):
        articles = response.xpath('//div[@class="titleNav"]/ul/li/a/@onclick').extract()
        for article in articles:
            path = re.findall('(?<=\').*(?=\',)', article)[0]
            url = self.base_url + path
            yield Request(url, self.article_parse)

    def article_parse(self, response):
        list_title = response.xpath('//*[@id="content"]/div/h1/text()').extract()
        title = "".join(list_title)
        list_content = response.xpath('//*[@id="content_div"]/p/font/text()').extract()
        content = "".join(list_content)
        list_date = re.findall('(?<=/)\d{1,}(?=/)', response.url)
        str_date = "".join(list_date)
        date = str_date[:4] + '-' +  str_date[4:6] + '-' + str_date[6:8]
        list_page_category = response.xpath('//*[@id="content"]/div/p[1]/text()[2]').extract()
        str_page_category = "".join(list_page_category)
        list_page = re.findall('\w{1,}', str_page_category, re.A)
        page = "".join(list_page)
        list_category = re.findall('(?<=:).*', str_page_category)
        category = "".join(list_category)
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
