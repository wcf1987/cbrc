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
import re
from bs4 import BeautifulSoup
import  settings
class cbrcPipeline(object):
    def process_item(self, item, spider):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'}
        req = urllib2.Request(url=item['url'],headers=headers)
        res = urllib2.urlopen(req)

        #print(requests.utils.get_encodings_from_content(page_content.text))
        #print os.getcwd()
        file_name = os.path.join(u'',os.getcwd(),'cbrc',settings.BaseDir,str(settings.CBRCLevels),item['urltitle'].strip()+'.html')
        #print file_name
        htmltext=res.read()
        #htmltext =unicode(htmltext, "gb2312")
        htmltext=htmltext.replace('charset=gb2312','charset=utf-8')
            #decode('gb2312','ignore')
        #print file_name
        with open(file_name,'wb') as fp:
            fp.write(htmltext)
        """Process each item process_item"""
        #self.parseHTML(res)
        query = self.__dbpool.runInteraction(self.__insertdata, item, spider,htmltext,file_name)
        query.addErrback(self.handle_error)
        return item
    def __init__(self):
        """Initialize"""
        self.__dbpool = adbapi.ConnectionPool('sqlite3',
                database=os.getcwd()+'/cbrc/database/cbrcpunish.db',
                check_same_thread=False)
    def shutdown(self):
        """Shutdown the connection pool"""
        self.__dbpool.close()

    def parseHTML(self,res,title,path):
        pc=punishcontent()
        pc.Punishfilename=title
        pc.localpath=path



        #print s2.get_text()
        #tree = etree.HTML(res)
        #print tree
        #strt=u"行政处罚决定书文号"
        #z=tree.xpath(u'//tr/td/p/span[contains(text(),"行政处罚决定书文号")]')
        #z = tree.xpath(u'//*[@id="doc"]/center/div[3]/div[1]/div/div/table/tbody/tr[1]/td/table/tbody/tr[2]/td/div/div/table/tbody/tr[1]/td[2]/p')
        soup = BeautifulSoup(res, "html.parser")
        s1=soup.find("span",text=["行政处罚决定书文号"])
        s2=s1.parent.parent.next_sibling
        #print s2.get_text()
        pc.DocumentNumber=s2.get_text().strip()
        s1=soup.find("span",text=["个人姓名"])
        s2=s1.parent.parent.next_sibling
        pc.PersonName=s2.get_text().strip()
        s1=soup.find("span",text=["名称"])
        s2=s1.parent.parent.next_sibling
        pc.OrgName=s2.get_text().strip()
        s1=soup.find("span",text=re.compile(u'法定代表人'))
        s2=s1.parent.parent.next_sibling
        pc.Legalrepresentative=s2.get_text().strip()



        s1=soup.find("span",text=re.compile(u'主要违法违规事实'))
        s2=s1.parent.parent.next_sibling
        pc.Causeofaction=s2.get_text().strip()

        s1 = soup.find("span", text=["行政处罚依据"])
        s2 = s1.parent.parent.next_sibling
        pc.Basisforpunishment=s2.get_text().strip()

        s1 = soup.find("span", text=["行政处罚决定"])
        s2 = s1.parent.parent.next_sibling
        pc.penaltydecision=s2.get_text().strip()

        s1 = soup.find("span", text=re.compile(u"作出处罚决定的"))
        s2 = s1.parent.parent.next_sibling
        pc.organmadepunishment=s2.get_text().strip()

        s1 = soup.find("span", text=["作出处罚决定的日期"])
        s2 = s1.parent.parent.next_sibling
        pc.Datedecisionpenalty=s2.get_text().strip()
        pc.levels=settings.CBRCLevels
        return pc
    def __insertdata(self,tx,item,spider,res,path):
        """Insert data into the sqlite3 database"""
        spidername=spider.name
        title=item['urltitle']

        tx.execute("select * from punishlist where Punishfilename = ?", (title,))
        result = tx.fetchone()
        if result:
            #print u"已插入记录：" + title
            #log.msg("Already exists in database", level=log.DEBUG)
            pass
        else:
            print u"开始解析记录：" + title
            #if title <> u'中国银监会行政处罚信息公开表（银监罚决字〔2017〕25号）':
                #return
            pc=self.parseHTML(res,title,path)
            try:
                tx.execute(\
                            "insert into punishlist(Punishfilename, localpath, DocumentNumber, PersonName, OrgName,Legalrepresentative,Causeofaction,Basisforpunishment,penaltydecision,organmadepunishment,Datedecisionpenalty,Levels) values (?,?,?,?,?,?,?,?,?,?,?)",(
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
                        pc.levels
                                        ))
                print u"插入记录："+pc.Punishfilename
                #log.msg("Item stored in db", level=log.DEBUG)
            except Exception  as e:
                print e.message
    def handle_error(self,e):
        pass
        #.err(e)