# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class MeiZhouDailySpider(scrapy.Spider):
    name = "meizhoudaily"
    allowed_domains = ["meizhou.cn"]
    base_url = "http://mzrb.meizhou.cn/"
    newspapers = "梅州日报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y-%m/%d')
        url = self.base_url + 'html/%s/node_1.htm' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        pages = response.xpath('//div[@id="pgn"]/ul/li/a/@href').extract()
        #当前页面没数据则重爬
        if response.status == 404 or  not pages:
            time.sleep(18) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for page in pages:
            page_index = re.findall('\d{1,}', page)
            url = re.sub('(?<=_)\d{1,}',page_index[0],response.url)
            yield Request(url, self.page_parse)

    def page_parse(self, response):
        articles = response.xpath('//div[@class="titlelist"]/table/tbody/tr/td[2]/a/@href').extract()
        for article in articles:
            url = re.sub('(node_\d{1,}\.htm)',article,response.url)
            yield Request(url, self.article_parse)

    def article_parse(self, response):
        list_title = response.xpath('//div[@class="middle"]/table[1]/tr[4]/td[2]/table[2]/tbody/tr/td/strong/text()').extract()
        title = "".join(list_title)
        list_page = response.xpath('//div[@class="middle"]/table[1]/tr[4]/td[2]/table[1]/tr[1]/td[1]/div/text()').extract()
        str_page = "".join(list_page)
        page = re.findall('\d{1,}', str_page)[0]
        list_content = response.xpath('//*[@id="ozoom"]/founder-content/p/text()').extract()
        content = "".join(list_content)
        list_date = re.findall('(?<=/)\d{1,}-\d{1,}/\d{1,}(?=/)', response.url)
        str_date = "".join(list_date)
        date = str_date.replace('/', '-')
        list_category = response.xpath('//div[@class="middle"]/table[1]/tr[4]/td[2]/table[1]/tr[1]/td[1]/div/strong/text()').extract()
        str_category = "".join(list_category)
        category = str_category.strip()
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
