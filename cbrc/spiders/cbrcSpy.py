# -*- coding: utf-8 -*-
import scrapy
import os
import sys

sys.path.append("..")
# 导入item中结构化数据模板
import cbrc.cbrcItem
from cbrc.settings import  *

class cbrcSpy(scrapy.Spider):
    # 爬虫名称，唯一
    name = "cbrcspyder"
    # 允许访问的域
    allowed_domains = ["cbrc.gov.cn"]
    # 初始URL
    start_urls = startURLs
    url_set = set()
    def checkLevel(self,url):
        if url.find("110002.html")>-1:
            return '1'
        if url.find("//1.html")>-1:
            return '2'
        if url.find("//2.html")>-1:
            return '3'
        return '4'

    def parse(self, response):
        # 获取所有图片的a标签
        #allFiles = response.xpath('//tr/td/a[re:test(@href,"^\/chinese\/home\/docView\/")]')
        #allFiles = response.xpath('//tr/td/a[starts-with(@href, "/chinese/home/docView/")]')
        allFiles = response.xpath('//table[contains(@id,"testUI")]/tr')
        level=self.checkLevel(response.url)
        for file in allFiles:
            # 分别处理每个连接，取出名称及地址
            item = cbrc.cbrcItem.cbrcItem()
            #print file['data']
            #print file.xpath('./td/a/@href').extract()
            if(len(file.xpath('./td/input').extract())==0):

                url=file.xpath('./td/a/@href').extract()[0]
                urltitle=file.xpath('./td/a/@title').extract()[0]
                url = 'http://www.cbrc.gov.cn' + url
                #print url
                #print urltitle
                item['url'] = url
                item['urltitle'] = urltitle
                item['level']=level
                yield item
            else:
                urls=file.xpath(u'./td/a[contains(text(),"下页")]/@href').extract()
                #.extract()[0]
                if len(urls)>0:
                    if level==1:
                        urln=urls[0]
                        urln = startURLs + urln
                    else:
                        urln = urls[0]
                        urln = "http://www.cbrc.gov.cn" + urln
                    if urln in cbrcSpy.url_set:
                        pass
                    else:
                        cbrcSpy.url_set.add(urln)
                            # 回调函数默认为parse,也可以通过from scrapy.http import Request来指定回调函数
                            # from scrapy.http import Request
                            # Request(url,callback=self.parse)
                        #yield self.make_requests_from_url(urln)
                        yield scrapy.Request(urln, callback=self.parse)
                #pass
            # 返回爬取到的数据


