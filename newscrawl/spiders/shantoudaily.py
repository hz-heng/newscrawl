# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class ShanTouDailySpider(scrapy.Spider):
    name = "shantoudaily"
    allowed_domains = ["dahuawang.com"]
    base_url = "http://strb.dahuawang.com/"
    newspapers = "汕头日报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y-%m/%d')
        url = self.base_url + 'html/%s/node_24.htm' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        pages = response.xpath('//*[@id="pageLink"]/@href').extract()
        #当前页面没数据则重爬
        if response.status == 404 or not pages:
            time.sleep(1800) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for page in pages:
            page_index = re.findall('\d{1,}', page)
            url = re.sub('(?<=_)\d{1,}',page_index[0],response.url)
            yield Request(url, self.page_parse, dont_filter=True)

    def page_parse(self, response):
        articles = response.xpath('//*[@id="btdh"]/table/tbody/tr/td[2]/a/@href').extract()
        for article in articles:
            url = re.sub('(node_\d{1,}\.htm)',article,response.url)
            yield Request(url, self.article_parse)

    def article_parse(self, response):
        list_title = response.xpath('//*[@id="logoTable"]/tr/td[2]/table[2]/tr[2]/td/div/table/tr/td/table/tr[1]/td/table/tbody/tr[2]/td/text()').extract()
        title = "".join(list_title)
        list_page = response.xpath('//*[@id="logoTable"]/tr/td[1]/table/tr[1]/td/table[2]/tr/td[2]/text()').extract()
        str_page = "".join(list_page)
        page = str_page.replace('：', '')
        list_content = response.xpath('//*[@id="ozoom"]/founder-content/p/text()').extract()
        content = "".join(list_content)
        list_date = re.findall('(?<=/)\d{1,}-\d{1,}/\d{1,}(?=/)', response.url)
        str_date = "".join(list_date)
        date = str_date.replace('/', '-')
        list_category = response.xpath('//*[@id="logoTable"]/tr/td[1]/table/tr[1]/td/table[2]/tr/td[2]/strong/text()').extract()
        str_category = "".join(list_category)
        category = str_category.replace(' ','')
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
