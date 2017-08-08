# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class ChaoZhouDailySpider(scrapy.Spider):
    name = "chaozhoudaily"
    allowed_domains = ["chaozhoudaily.com"]
    base_url = "http://www.chaozhoudaily.com/"
    newspapers = "潮州日报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y-%m/%d')
        url = self.base_url + 'czrb/html/%s/node_2.htm' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        pages = response.xpath('//*[@id="bmdh"]/table/tbody/tr/td/a/@href').extract()
        #当前页面没数据则重爬
        if response.status == 404 or  not pages:
            time.sleep(1800) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for page in pages:
            page_path = re.findall('(?<=_)\w{1,}(?=.htm)', page)
            url = re.sub('(?<=_)\w{1,}(?=.htm)',page_path[0],response.url)
            yield Request(url, self.page_parse, dont_filter=True)

    def page_parse(self, response):
        articles = response.xpath('//*[@id="btdh"]/table/tbody/tr/td/a/@href').extract()
        for article in articles:
            url = re.sub('node_\d{1,}.htm',article, response.url)
            yield Request(url, self.article_parse)

    def article_parse(self, response):
        list_title = response.xpath('//td[@class="font01"]/text()').extract()
        title = "".join(list_title).strip()
        list_content = response.xpath('//*[@id="ozoom"]/founder-content/p/text()').extract()
        content = "".join(list_content).strip()
        list_date = re.findall('(?<=/)\d{1,}-\d{1,}/\d{1,}(?=/)', response.url)
        str_date = "".join(list_date)
        date = str_date.replace('/','-')
        list_page = response.xpath('//*[@id="logoTable"]/tr/td[1]/table/tr[1]/td/table[2]/tr/td[2]/text()').extract()
        str_page = "".join(list_page)
        page = re.findall('\w{1,}', str_page, re.A)[0]
        list_category = response.xpath('//*[@id="logoTable"]/tr/td[1]/table/tr[1]/td/table[2]/tr/td[2]/strong/text()').extract()
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
