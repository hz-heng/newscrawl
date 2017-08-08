# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class QingYuanDailySpider(scrapy.Spider):
    name = "qingyuandaily"
    allowed_domains = ["qyrb.com"]
    base_url = "http://epaper.qyrb.com:7777/"
    newspapers = "清远日报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y%m%d')
        url = self.base_url + 'content/%s/PageArticleIndexLB.htm' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        pages = response.xpath('/html/body/table/tbody/tr/td/p/a/@href').extract()
        #当前页面没数据则重爬
        if response.status == 404 or  not pages:
            time.sleep(1800) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for page in pages:
            page_path = re.findall('\w{1,}(?=.htm)', page)
            url = re.sub('(?<=/)\w{1,}(?=.htm)',page_path[0],response.url)
            yield Request(url, self.page_parse)

    def page_parse(self, response):
        articles = response.xpath('//*[@id="mylink"]/a/@href').extract()
        for article in articles:
            article_path = re.findall('\w{1,}(?=.htm)', article)
            url = re.sub('(?<=/)\w{1,}(?=.htm)',article_path[0], response.url)
            yield Request(url, self.article_parse)

    def article_parse(self, response):
        list_title = response.xpath('//div[@class="detailtitle"]/text()').extract()
        title = "".join(list_title).strip()
        list_content = response.xpath('//*[@id="contenttext"]/text()').extract()
        content = "".join(list_content).strip()
        list_date = re.findall('(?<=/)\d{1,}(?=/)', response.url)
        str_date = "".join(list_date)
        date = str_date[:4] + '-' + str_date[4:6] + '-' + str_date[6:8]
        list_page_category = response.xpath('/html/body/div[1]/table[1]/tbody/tr/td[2]/table[2]/tbody/tr[1]/td/div/strong[1]/font/text()').extract()
        str_page_category = "".join(list_page_category)
        page = re.findall('\w{1,}', str_page_category, re.A)[0]
        category = str_page_category.split(':')[1]
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
