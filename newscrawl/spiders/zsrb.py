# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime, timedelta
from newscrawl.items import newsItem
import time


class ZsrbSpider(scrapy.Spider):
    name = "zsrb"
    allowed_domains = ["zsnews.cn"]
    #start_urls = ['http://zsnews.cn/']
    base_url = "http://epaper.zsnews.cn/zsrb/"
    today = datetime.today()

    def start_requests(self):
        for i in range(1):
            date = self.today - timedelta(days=i)
            sdate = date.strftime('%Y%m%d')
            url = self.base_url + 'ShowIndex.asp?paperdate=%s' % sdate
            yield Request(url, self.parse)

    def parse(self, response):
        pages = response.xpath('//*[@id="FastEditionList"]/table/tr/td[@onclick]/@onclick').extract()
        #当前页面没数据则重爬
        if not pages:
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
        item = newsItem()
        list_title = response.xpath('//td[@id="ContentArea_ArticleTitle_Title"]/text()').extract()
        title = "".join(list_title)
        #list_author = response.xpath('//div[@id="ContentArea_ArticleSource"]/text()').extract()
        list_page = response.xpath('//span[@id="ArticlePageHead_thisPage"]/text()').extract()
        page = "".join(list_page)
        list_content = response.xpath('//td[@id="ContentArea_ArticleContent"]/text()').extract()
        content = "".join(list_content)
        list_issue_date = response.xpath('//span[@id="ArticlePageHead_thisPaperDate"]/text()').extract()
        str_issue_date = "".join(list_issue_date)
        issue_date = str_issue_date.replace('/', '-')
        list_category = response.xpath('//span[@id="ArticlePageHead_thisNote"]/text()').extract()
        category = "".join(list_category)
        if content == "":
            pass
        else:
            item['title'] = title
            item['page'] = page
            item['content'] = content
            item['issue_date'] = issue_date
            item['category'] = category
            yield item
