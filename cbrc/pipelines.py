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
    def __init__(self):
        """Initialize"""
        self.__dbpool = adbapi.ConnectionPool('sqlite3',
                database=os.getcwd()+'/cbrc/database/cbrcpunish.db',
                check_same_thread=False)
    def shutdown(self):
        """Shutdown the connection pool"""
        self.__dbpool.close()
    def process_item(self, item, spider):

        file_name = os.path.join(u'',os.getcwd(),'cbrc',settings.BaseDir,str(item['level']),item['urltitle'].strip()+'.html')
        htmltext=""
        if not self.checkfileExists(file_name):
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'}
            req = urllib2.Request(url=item['url'], headers=headers)
            res = urllib2.urlopen(req)
            htmltext = res.read()
            htmltext = htmltext.replace('charset=gb2312', 'charset=utf-8')
            with open(file_name,'wb') as fp:
                fp.write(htmltext)
            print u"保存文件："+file_name
        else:
            #f = open(file_name, 'r')
            #htmltext = f.read()
            pass
        #query = self.__dbpool.runInteraction(self.__insertdata, item, spider,htmltext,file_name)
        #query.addErrback(self.handle_error)
        return item


    def checkfileExists(self,filepath):
        return os.path.exists(filepath)

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
            pc=self.parseHTMLByTEXT(res,title,path)
            try:
                tx.execute(\
                            "insert into punishlist(Punishfilename, localpath, DocumentNumber, PersonName, OrgName,Legalrepresentative,Causeofaction,Basisforpunishment,penaltydecision,organmadepunishment,Datedecisionpenalty,Levels) values (?,?,?,?,?,?,?,?,?,?,?,?)",(
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

    def parseHTMLByTEXT(self,res,title,path):
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
        s1=soup.find("table",attrs={"class":"MsoNormalTable"})
        s2=s1.get_text()

        searchText=[u"行政处罚决定书文号",u"被处罚当事人姓名或名称个人姓名",u"单位名称",u"法定代表人（主要负责人）姓名",u"主要违法违规事实（案由）",u"行政处罚依据",u"行政处罚决定",u"作出处罚决定的机关名称",u"作出处罚决定的日期",u"插入记录"]
        resultsText=[]
        indexStart=0
        for i in range(len(searchText)-1):
            indexStart=s2.find(searchText[i],indexStart)+len(searchText[i])
            indexEnd=s2.find(searchText[i+1],indexStart)
            s3=s2[indexStart:indexEnd]
            resultsText.append(s3)
        pc.DocumentNumber = resultsText[0]

        pc.PersonName =resultsText[1]

        pc.OrgName =resultsText[2]

        pc.Legalrepresentative =resultsText[3]


        pc.Causeofaction =resultsText[4]


        pc.Basisforpunishment =resultsText[5]

        pc.penaltydecision = resultsText[6]


        pc.organmadepunishment = resultsText[7]


        pc.Datedecisionpenalty = resultsText[8]
        pc.levels = settings.CBRCLevels
        return pc