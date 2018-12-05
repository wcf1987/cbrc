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

class DbSqlitePipeline(object):
    def __init__(self):
        """Initialize"""
        self.__dbpool = adbapi.ConnectionPool('sqlite3',
                database='/datebase/sqlite.db',
                check_same_thread=False)
    def shutdown(self):
        """Shutdown the connection pool"""
        self.__dbpool.close()
    def process_item(self,item,spider):
        """Process each item process_item"""
        query = self.__dbpool.runInteraction(self.__insertdata, item, spider)
        query.addErrback(self.handle_error)
        return item
    def __insertdata(self,tx,item,spider):
        """Insert data into the sqlite3 database"""
        spidername=spider.name
        for img in item['images']:
            tx.execute("select * from data where url = ?", (img['url'],))
            result = tx.fetchone()
            if result:
                log.msg("Already exists in database", level=log.DEBUG)
            else:
                tx.execute(\
                        "insert into data(url, localpath, checksum, created, spidername) values (?,?,?,?,?)",(
                            img['url'],
                            img['path'],
                            img['checksum'],
                            time.time(),
                            spidername)
                        )
                log.msg("Item stored in db", level=log.DEBUG)
    def handle_error(self,e):
        log.err(e)