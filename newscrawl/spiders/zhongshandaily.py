# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class ZhongShanDailySpider(scrapy.Spider):
    name = "zhongshandaily"
    allowed_domains = ["zsnews.cn"]
    base_url = "http://epaper.zsnews.cn/zsrb/"
    newspapers = "中山日报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y%m%d')
        url = self.base_url + 'ShowIndex.asp?paperdate=%s' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        pages = response.xpath('//*[@id="FastEditionList"]/table/tr/td[@onclick]/@onclick').extract()
        #当前页面没数据则重爬
        if response.status == 404 or not pages:
            time.sleep(1800) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for page in pages:
            page_index = re.findall('\d{1,}', page)
            url = self.base_url + 'ShowIndex.asp?paperdate=%s&part=%s' % (page_index[0], page_index[1])
            yield Request(url, self.page_parse)

    def page_parse(self, response):
        articles = response.xpath('//*[@id="TitleList"]/table/tr/td[@class="Title"]/a/@href').extract()
        for article in articles:
            url = self.base_url + article
            yield Request(url, self.article_parse)

    def article_parse(self, response):
        list_title = response.xpath('//td[@id="ContentArea_ArticleTitle_Title"]/text()').extract()
        title = "".join(list_title)
        list_page = response.xpath('//span[@id="ArticlePageHead_thisPage"]/text()').extract()
        page = "".join(list_page)
        list_content = response.xpath('//td[@id="ContentArea_ArticleContent"]/text()').extract()
        content = "".join(list_content)
        list_date = response.xpath('//span[@id="ArticlePageHead_thisPaperDate"]/text()').extract()
        str_date = "".join(list_date)
        date = str_date.replace('/', '-')
        list_category = response.xpath('//span[@id="ArticlePageHead_thisNote"]/text()').extract()
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
