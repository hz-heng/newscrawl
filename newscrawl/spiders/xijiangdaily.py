# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class XiJiangDailySpider(scrapy.Spider):
    name = "xijiangdaily"
    allowed_domains = ["xjrb.com"]
    base_url = "http://xjrb.xjrb.com:8000"
    newspapers = "西江日报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y/%m/%d')
        url = self.base_url + '/epaper/xjrb/%s/pub_index.html' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        pages = response.xpath('//span[@class="listTitle"]/a/@href').extract()
        #当前页面没数据则重爬
        if response.status == 404 or not pages:
            time.sleep(1800) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for page in pages:
            url = self.base_url + page
            yield Request(url, self.page_parse)

    def page_parse(self, response):
        articles = response.xpath('//div[@class="humor"]/ul/li/a/@href').extract()
        for article in articles:
            url = re.sub('(\d{1,}\.shtml)',article,response.url)
            print(url)
            yield Request(url, self.article_parse)

    def article_parse(self, response):
        list_title = response.xpath('//p[@class="articleTitle"]/text()').extract()
        title = "".join(list_title)
        list_page = response.xpath('//div[@class="leftTitle"]/text()').extract()
        str_page = "".join(list_page)
        page = str_page.split("：")[1]
        list_content = response.xpath('//div[@class="articleContent"]/p/text()').extract()
        content = "".join(list_content)
        list_date = re.findall('(?<=/)\d{1,}/\d{1,}/\d{1,}(?=/)', response.url)
        str_date = "".join(list_date)
        date = str_date.replace('/', '-')
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
