# -*- coding: utf-8 -*-
import scrapy
import os
# 导入item中结构化数据模板
import cbrc.cbrcItem


class cbrcSpy(scrapy.Spider):
    # 爬虫名称，唯一
    name = "cbrcspyder"
    # 允许访问的域
    allowed_domains = ["cbrc.gov.cn"]
    # 初始URL
    start_urls = ['http://www.cbrc.gov.cn/chinese/home/docViewPage/110002.html']
    url_set = set()
    def parse(self, response):
        # 获取所有图片的a标签
        #allFiles = response.xpath('//tr/td/a[re:test(@href,"^\/chinese\/home\/docView\/")]')
        #allFiles = response.xpath('//tr/td/a[starts-with(@href, "/chinese/home/docView/")]')
        allFiles = response.xpath('//table[contains(@id,"testUI")]/tr')
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
            else:
                urln=file.xpath(u'./td/a[contains(text(),"下")]/@href').extract()[0]
                #.extract()[0]
                urln = 'http://www.cbrc.gov.cn/chinese/home/docViewPage/' + urln

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
            yield item

        def parseNext(next):
            url = next

            # 如果地址以http://www.xiaohuar.com/list-开头且不在集合中，则获取其信息
            if url.startswith("http://www.xiaohuar.com/list-"):
                if url in cbrcSpy.url_set:
                    pass
                else:
                    cbrcSpy.url_set.add(url)
                    # 回调函数默认为parse,也可以通过from scrapy.http import Request来指定回调函数
                    # from scrapy.http import Request
                    # Request(url,callback=self.parse)
                    yield self.make_requests_from_url(url)
            else:
                pass

        def parsePunishUrl(url):
            pass