# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class JiangMenDailySpider(scrapy.Spider):
    name = "jiangmendaily"
    allowed_domains = ["jmrb.com"]
    base_url = "http://dzb.jmrb.com:8080/"
    newspapers = "江门日报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y-%m/%d')
        url = self.base_url + 'jmrb/html/%s/node_22.htm' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        pages = response.xpath('//*[@id="pageLink"]/@href').extract()
        #当前页面没数据则重爬
        if response.status == 404 or  not pages:
            time.sleep(1800) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for page in pages:
            page_index = re.findall('\d{1,}', page)
            url = re.sub('(?<=_)\d{1,}',page_index[0],response.url)
            yield Request(url, self.page_parse, dont_filter=True)

    def page_parse(self, response):
        articles = response.xpath('/html/body/table/tr[1]/td[1]/table/tr[1]/td/table[3]/tr/td/table/tbody/tr/td/a/@href').extract()
        for article in articles:
            url = re.sub('(node_\d{1,}\.htm)',article,response.url)
            yield Request(url, self.article_parse)

    def article_parse(self, response):
        list_title = response.xpath('/html/body/table/tr[1]/td[2]/table[3]/tr[1]/td/table/tbody/tr/td/strong/text()').extract()
        str_title = "".join(list_title)
        title = str_title.strip()
        list_page = response.xpath('/html/body/table/tr[1]/td[1]/table/tr/td/table[2]/tr/td[1]/text()').extract()
        str_page = "".join(list_page)
        page = re.findall('\w{1,}', str_page, re.A)[0]
        list_content = response.xpath('//div[@id="ozoom"]/p/text()').extract()
        content = "".join(list_content)
        list_date = re.findall('(?<=/)\d{1,}-\d{1,}/\d{1,}(?=/)', response.url)
        str_date = "".join(list_date)
        date = str_date.replace('/', '-')
        list_category = response.xpath('/html/body/table/tr[1]/td[1]/table/tr/td/table[2]/tr/td[1]/strong/text()').extract()
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
