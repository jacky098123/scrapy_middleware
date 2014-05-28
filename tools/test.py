import os
import sys
import re
import pdb
import logging
import urllib2
import cookielib
import time
import traceback
from datetime import datetime
from optparse import OptionParser

from scrapy.selector import HtmlXPathSelector

sys.path.append('/home/yangrq/projects/pycore')
from utils.common_handler import CommonHandler
from utils.btlog import btlog_init
from db.mysqlv6 import MySQLOperator

from baidu_common import BaiduCommon
from config import *


class ProxyVerifier(CommonHandler):
    def __init__(self):
        self.crawled_proxys = []

        parser          = OptionParser()
        parser.add_option("--gen", action="store_true")
        parser.add_option("--flag", action="store", default='')
        parser.add_option("--hidemyass", action="store_true")
        parser.add_option("--free_proxy_list", action="store_true")
        parser.add_option("--freeproxylists", action="store_true")
        (self.opt, others) = parser.parse_args()

        self.db_conn = MySQLOperator()
        if not self.db_conn.Connect(**DB_CONF):
            logging.error("db error")
            sys.exit()

    def real_verify(self, ip, port):
        ip  = self.ToString(ip)
        if len(ip.split('.')) != 4:
            logging.warn("ip is bad: %s" % (ip))
            return 'bad'

        port = self.ToString(port)
        if not port.isdigit():
            logging.warn("port is bad: %s" % (port))
            return 'bad'

        tmp_proxy = "http://%s:%s" % (ip, port)
        return self._real_verify(tmp_proxy)

    def _real_verify(self, tmp_proxy):
        proxy_support = urllib2.ProxyHandler({'http': tmp_proxy})
        opener =urllib2.build_opener(proxy_support, urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0')]
        urllib2.install_opener(opener)

        succeed_count = 0
        for i in range(10):
            time.sleep(0.2)
            try:
                url = BaiduCommon.random_request()
                print url
                html = urllib2.urlopen(url, timeout=3).read()
                if len(html) > 100:
                    parse_dict = BaiduCommon.parse(html)
                    if parse_dict['valid_flag']:
                        succeed_count += 1
            except Exception, e:
                logging.warn("error: %s" % str(e))
        kxflag = ''
        if succeed_count == 0:
            kxflag = 'bad'
        elif succeed_count < 6:
            kxflag = 'pool'
        elif succeed_count < 9:
            kxflag = 'moderate'
        else:
            kxflag = 'good'
        logging.info("proxy: %s, succeed_count: %d" % (tmp_proxy, succeed_count))
        return kxflag

    def test(self):
        proxy_list = ['http://140.120.94.26:8088', 'http://181.208.70.75:8080']
        for proxy in proxy_list:
            self._real_verify(proxy)

if __name__ == '__main__':
    btlog_init('log_verifier.log', logfile=True, console=True, level='DEBUG')
    v = ProxyVerifier()
    v.test()
