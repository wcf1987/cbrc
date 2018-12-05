# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib2
import os

class cbrcPipeline(object):
    def process_item(self, item, spider):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'}
        req = urllib2.Request(url=item['url'],headers=headers)
        res = urllib2.urlopen(req)
        file_name = os.path.join(r'D:\profit\PYProjects\cbrc\cbrc\CBRCresults\\',item['urltitle']+'.html')
        with open(file_name,'wb') as fp:
            fp.write(res.read())
