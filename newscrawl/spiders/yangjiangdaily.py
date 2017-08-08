# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
from datetime import datetime
from newscrawl.items import newsItem
import time


class YangJiangDailySpider(scrapy.Spider):
    name = "yangjiangdaily"
    allowed_domains = ["yjrb.com.cn"]
    base_url = "http://yjdaily.yjrb.com.cn/"
    newspapers = "阳江日报"
    today = datetime.today()

    def start_requests(self):
        date = self.today
        sdate = date.strftime('%Y-%m/%d')
        url = self.base_url + 'html/%s/node_1.htm' % sdate
        yield Request(url, self.parse)

    def parse(self, response):
        pages = response.xpath('//*[@id="scrollDiv"]/table/tbody/tr/td[1]/a/@href').extract()
        #当前页面没数据则重爬
        if response.status == 404 or  not pages:
            time.sleep(1800) #等待30分钟
            yield Request(response.url, self.parse, dont_filter=True) #设置不过滤URL(实现不过滤重复URL)
        for page in pages:
            page_index = re.findall('\d{1,}', page)
            url = re.sub('(?<=_)\d{1,}',page_index[0],response.url)
            yield Request(url, self.page_parse, dont_filter=True)

    def page_parse(self, response):
        articles = response.xpath('//*[@id="main-ed-articlenav-list"]/table/tbody/tr/td[2]/div/a/@href').extract()
        for article in articles:
            url = re.sub('(node_\d{1,}\.htm)',article,response.url)
            yield Request(url, self.article_parse)

    def article_parse(self, response):
        list_title = response.xpath('//founder-title/text()').extract()
        title = "".join(list_title).strip()
        list_content = response.xpath('//*[@id="ozoom"]/founder-content/text()|//*[@id="ozoom"]/founder-content/p/text()').extract()
        content = "".join(list_content).strip()
        list_date = re.findall('(?<=/)\d{1,}-\d{1,}/\d{1,}(?=/)', response.url)
        str_date = "".join(list_date)
        date = str_date.replace('/', '-')
        list_category = response.xpath('/html/body/table[1]/tr[1]/td[1]/table/tr[1]/td/table[2]/tr/td[1]/strong/text()').extract()
        category = "".join(list_category)
        list_page = response.xpath('/html/body/table[1]/tr[1]/td[1]/table/tr[1]/td/table[2]/tr/td[1]/text()').extract()
        str_page = "".join(list_page)
        page = re.findall('\d{1,}', str_page)[0]
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
