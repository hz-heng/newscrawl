# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from datetime import datetime
from newscrawl.items import newsItem
import time


class ZhongShanDailySpider(scrapy.Spider):
    name = "zhongshandaily"
    allowed_domains = ["zsnews.cn"]
    base_url = "http://www.zsnews.cn/EPaper/zsrb/"
    newspapers = "中山日报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y%m%d')
        url = self.base_url + 'ShowIndex.asp?paperdate=%s' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        pages = response.xpath('//*[@id="FastEditionList"]/table/tr/td/a/@href').extract()
        #当前页面没数据则重爬
        if response.status == 404 or not pages:
            time.sleep(1800) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for page in pages:
            url = self.base_url + page
            yield Request(url, self.page_parse)

    def page_parse(self, response):
        articles = response.xpath('//*[@id="TitleList"]/table/tr/td[@class="Title"]/a/@href').extract()
        for article in articles:
            url = self.base_url + article
            yield Request(url, self.article_parse)

    def article_parse(self, response):
        title = response.xpath('//td[@id="ContentArea_ArticleTitle_Title"]/text()').extract_first()
        page = response.xpath('//span[@id="ArticlePageHead_thisPage"]/text()').extract_first()
        content = response.xpath('//td[@id="ContentArea_ArticleContent"]/text()').extract_first()
        str_date = response.xpath('//span[@id="ArticlePageHead_thisPaperDate"]/text()').extract_first()
        date = str_date.replace('/', '-')
        category = response.xpath('//span[@id="ArticlePageHead_thisNote"]/text()').extract_first()
        if content != "":
            item = newsItem()
            item['title'] = title
            item['page'] = page
            item['content'] = content
            item['date'] = date
            item['category'] = category
            item['url'] = response.url
            item['newspapers'] = self.newspapers
            yield item
