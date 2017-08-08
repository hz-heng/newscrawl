# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class HuiZhouDailySpider(scrapy.Spider):
    name = "huizhoudaily"
    allowed_domains = ["hznews.com"]
    base_url = "http://e.hznews.com"
    newspapers = "惠州日报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y%m%d')
        url = self.base_url + '/paper/hzrb/%s/' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        pages = response.xpath('//div[@class="list_r"]/div/ul/li/a/@href').extract()
        #当前页面没数据则重爬
        if response.status == 404 or  not pages:
            time.sleep(1800) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for page in pages:
            url = self.base_url + page
            yield Request(url, self.page_parse)

    def page_parse(self, response):
        articles = response.xpath('//div[@class="list_l"]/div/ul/li/a/@href').extract()
        for article in articles:
            url = self.base_url + article
            yield Request(url, self.article_parse)

    def article_parse(self, response):
        list_title = response.xpath('//div[@class="content"]/h2/text()').extract()
        title = "".join(list_title)
        list_page = re.findall('(?<=/)[A-Z]\d{1,}(?=/)', response.url)
        page = "".join(list_page)
        list_content = response.xpath('//div[@class="cnt-main"]/p/text()').extract()
        content = "".join(list_content)
        list_issue_date = re.findall('(?<=/)\d{1,}(?=/)', response.url)
        str_date = "".join(list_date)
        date = str_date[:4] + '-' + str_date[4:6] + '-' + str_date[6:8]
        list_category = response.xpath('//div[@class="info"]/span[2]/a/text()').extract()
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
