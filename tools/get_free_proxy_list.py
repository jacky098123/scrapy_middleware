import os
import sys
import re
import pdb
import logging
import urllib2
import cookielib
import time
import traceback
from optparse import OptionParser
from datetime import datetime

from scrapy.selector import HtmlXPathSelector
from bs4 import BeautifulSoup

sys.path.append('/home/yangrq/projects/pycore')
from utils.common_handler import CommonHandler
from utils.btlog import btlog_init
from db.mysqlv6 import MySQLOperator

from config import *


class ProxyDownloader(CommonHandler):
    def __init__(self,):
        self.crawled_proxys = []

        parser          = OptionParser()
        parser.add_option("--proxy", action="store", default="http://127.0.0.1:8087")
        parser.add_option("--try_times", action="store", default="5")
        parser.add_option("--cache", action="store_true")
        (self.opt, others) = parser.parse_args()

        if not self.opt.proxy.startswith('http://'):
            logging.error("proxy should startswith http://")
            sys.exit()

        if self.opt.proxy:
            proxy_support = urllib2.ProxyHandler({'http':self.opt.proxy})
            opener =urllib2.build_opener(proxy_support, urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0')]
            urllib2.install_opener(opener)

        self.db_conn = MySQLOperator()
        if not self.db_conn.Connect(**DB_CONF):
            logging.error("db error")
            sys.exit()


    def _url2file(self, url, suffix='html'):
        import hashlib
        m = hashlib.md5()
        m.update(url)

        if not os.access('cache', os.F_OK):
            os.mkdir('cache')
        f = "cache/%s.%s" % (m.hexdigest(), suffix)
        logging.info("[%s] ==> [%s]" % (url, f))
        return f

    def _crawl_url(self, url):
        logging.info("_crawl_url ")
        content = ""
        request = urllib2.Request(
                url     = url,
                headers = {'Content-Type':'application/x-www-form-urlencoded','charset':'UTF-8'}
            )

        for i in range(int(self.opt.try_times)):
            try:
                o =urllib2.urlopen(request)
                if o.code / 100 == 2:
                    content = o.read()
            except Exception, e:
                logging.warn("e str: %s" % str(e))
            if len(content) > 100:
                break
            time.sleep(3)

        if len(content) > 0:
            f = self._url2file(url)
            self.SaveFile(f, content)
            logging.info("save to %s" % f)
        return content


    def do_free_proxy_list(self):
        url = "http://free-proxy-list.net/"
        content = self._crawl_url(url)

        hxs = HtmlXPathSelector(text=content)
        tr_selectors = hxs.select(".//*[@id='proxylisttable']/tbody/tr")
        if len(tr_selectors) == 0:
            logging.warn("find data error")
            return

        logging.info("count: %d for url: %s" % (len(tr_selectors), url))
        for selector in tr_selectors:
            data_list = selector.select(".//td/text()").extract()
            db_data             = {}
            db_data['ip']       = data_list[0]
            db_data['port']     = data_list[1]
            db_data['code']     = data_list[2]
            db_data['country']  = data_list[3]
            db_data['anonymity']= data_list[4]
            db_data['google']   = data_list[5]
            db_data['https']    = data_list[6]

            self.db_conn.Upsert('proxy_free_proxy_list', db_data, ['ip','port'])

    def run(self):
        self.do_free_proxy_list()

if __name__ == '__main__':
    btlog_init('log_download.log', logfile=True, console=True)
    d = ProxyDownloader()
    d.run()
