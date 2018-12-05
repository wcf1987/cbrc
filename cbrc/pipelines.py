# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import urllib2
import os
from scrapy import log
from twisted.enterprise import adbapi

import time
import sqlite3
from cbrc.punishcontent import punishcontent
import codecs
from lxml import etree
import sys

class cbrcPipeline(object):
    def process_item(self, item, spider):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'}
        req = urllib2.Request(url=item['url'],headers=headers)
        res = urllib2.urlopen(req)

        #print(requests.utils.get_encodings_from_content(page_content.text))
        file_name = os.path.join(r'D:\profit\PYProjects\cbrc\cbrc\CBRCresults\\',item['urltitle']+'.html')
        htmltext=res.read()
        #htmltext =unicode(htmltext, "gb2312")
        htmltext=htmltext.replace('charset=gb2312','charset=utf-8')
            #decode('gb2312','ignore')
        print htmltext
        #with open(file_name,'wb') as fp:
            #fp.write(htmltext)
        """Process each item process_item"""
        #self.parseHTML(res)
        query = self.__dbpool.runInteraction(self.__insertdata, item, spider,htmltext,file_name)
        query.addErrback(self.handle_error)
        return item
    def __init__(self):
        """Initialize"""
        self.__dbpool = adbapi.ConnectionPool('sqlite3',
                database='D:/profit/PYProjects/cbrc/cbrc/database/cbrcpunish.db',
                check_same_thread=False)
    def shutdown(self):
        """Shutdown the connection pool"""
        self.__dbpool.close()

    def parseHTML(self,res,title,path):
        pc=punishcontent()
        pc.Punishfilename=title
        pc.localpath=path

        tree = etree.HTML(res)
        #print tree
        #strt=u"行政处罚决定书文号"
        z=tree.xpath(u'//span[contains(text(),"行政处罚决定书文号")]')
        #z = tree.xpath(u'//span/text()')
        pc.DocumentNumber=z
        pc.PersonName
        pc.OrgName
        pc.Legalrepresentative
        pc.Causeofaction
        pc.Basisforpunishment
        pc.penaltydecision
        pc.organmadepunishment
        pc.Datedecisionpenalty
        pc.id=1
        return pc
    def __insertdata(self,tx,item,spider,res,path):
        """Insert data into the sqlite3 database"""
        spidername=spider.name
        title=item['urltitle']
        tx.execute("select * from punishlist where Punishfilename = ?", (title,))
        result = tx.fetchone()
        if result:
            log.msg("Already exists in database", level=log.DEBUG)
        else:
            pc=self.parseHTML(res,title,path)
            tx.execute(\
                        "insert into punishlist(Punishfilename, localpath, DocumentNumber, PersonName, OrgName,Legalrepresentative,Causeofaction，Basisforpunishment，penaltydecision，organmadepunishment，Datedecisionpenalty，id) values (?,?,?,?,?,?,?,?,?,?,?,?)",(
                    pc.Punishfilename,
                    pc.localpath ,
                    pc.DocumentNumber ,
                    pc.PersonName ,
                    pc.OrgName ,
                    pc.Legalrepresentative ,
                    pc.Causeofaction ,
                    pc.Basisforpunishment ,
                    pc.penaltydecision ,
                    pc.organmadepunishment ,
                    pc.Datedecisionpenalty ,
                    pc.id                         ))
            log.msg("Item stored in db", level=log.DEBUG)
    def handle_error(self,e):
        log.err(e)