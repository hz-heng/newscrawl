# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class ShenZhenDailySpider(scrapy.Spider):
    name = "shenzhendaily"
    allowed_domains = ["sznews.com"]
    base_url = "http://sztqb.sznews.com/"
    newspapers = "深圳特区报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y%m/%d')
        url = self.base_url + 'PC/layout/%s/colA01.html' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        areas = response.xpath('//div[@class="Chunkiconlist"]/p/a[1]')
        #当前页面没数据则重爬
        if response.status == 404 or  not areas:
            time.sleep(18) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for area in areas:
            page = area.xpath('@href').extract()[0]
            url = re.sub('\w{1,}.html',page,response.url)
            str_category = area.xpath('text()').extract()[0]
            category = str_category.split('：')[1]
            yield Request(url, self.page_parse, dont_filter=True, meta={'category':category})

    def page_parse(self, response):
        articles = response.xpath('//div[@class="newslist"]/ul/li/h3/a/@href').extract()
        category = response.meta['category']
        for article in articles:
            article_path = re.findall('/\w{1,}/\w{1,}/\w{1,}/\w{1,}.html', article)[0]
            url = self.base_url + 'PC' + article_path
            yield Request(url, self.article_parse, meta={'category':category})

    def article_parse(self, response):
        list_title = response.xpath('//div[@class="newsdetatit"]/h3/text()').extract()
        title = "".join(list_title).strip()
        list_content = response.xpath('//div[@class="newsdetatext"]/founder-content/p/text()').extract()
        content = "".join(list_content).strip()
        list_date = re.findall('(?<=/)\d{1,}/\d{1,}(?=/)', response.url)
        str_date = "".join(list_date)
        n_date = str_date.replace('/','-')
        date = n_date[:4] + '-' + n_issue_date[4:]
        list_page = response.xpath('//div[@class="newsdetatit"]/p[3]/span[@class="Author"]/text()').extract()
        str_page = "".join(list_page)
        page = str_page.split('：')[1]
        if content == "":
            pass
        else:
            item = newsItem()
            item['title'] = title
            item['page'] = page
            item['content'] = content
            item['date'] = date
            item['category'] = response.meta['category']
            item['url'] = response.url
            item['newspapers'] = self.newspapers
            yield item
