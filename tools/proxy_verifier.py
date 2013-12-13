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

from scrapy.selector import HtmlXPathSelector
from bs4 import BeautifulSoup

sys.path.append('/home/yangrq/projects/pycore')
from utils.common_handler import CommonHandler
from utils.btlog import btlog_init
from db.mysqlv6 import MySQLOperator

DB_CONF = {
    "host"  : "192.168.0.57",
    "user"  : "product_w",
    "passwd": "kooxootest",
    "database"  : "proxy",
    "port"      : 3306,
    "charset"   : "utf8"
}

class ProxyVerifier(CommonHandler):
    def __init__(self):
        self.crawled_proxys = []

        parser          = OptionParser()
        parser.add_option("--full", action="store_true")
        parser.add_option("--gen", action="store_true")
        (self.opt, others) = parser.parse_args()

        self.db_conn = MySQLOperator()
        if not self.db_conn.Connect(**DB_CONF):
            logging.error("db error")
            sys.exit()

    def _update_hidemyass(self, id, kxflag):
        sql = "update proxy_hidemyass set kxflag=%s where id=" + str(id)
        logging.info("%s, [%s]" % (sql, kxflag))
        self.db_conn.Execute(sql, [kxflag,])

    def verify_hidemyass(self, row):
        ip_items = row['ip'].split('.')
        if len(ip_items) != 4:
            logging.warn("ip is bad: %s, id: %d" % (row['ip'], row['id']))
            self._update_hidemyass(row['id'], 'bad')
            return

        tmp_port = self.ToString(row['port'])
        if not tmp_port.isdigit():
            logging.warn("port is bad: %s, id: %d" % (row['port'], row['id']))
            self._update_hidemyass(row['id'], 'bad')
            return

        tmp_proxy = "http://%s:%s" % (row['ip'], row['port'])
        proxy_support = urllib2.ProxyHandler({'http': tmp_proxy})
        opener =urllib2.build_opener(proxy_support, urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0')]
        urllib2.install_opener(opener)

        succeed_count = 0
        for i in range(10):
            time.sleep(1)
            try:
                html = urllib2.urlopen("http://www.baidu.com/", timeout=10).read()
                if len(html) > 100:
                    succeed_count += 1
            except Exception, e:
                logging.warn("error: %s" % str(e))
        kxflag = ''
        if succeed_count == 0:
            kxflag = 'bad'
        elif succeed_count < 3:
            kxflag = 'pool'
        elif succeed_count < 7:
            kxflag = 'moderate'
        else:
            kxflag = 'good'
        logging.info("ip: %s, port: %s, succeed_count: %d" % (row['ip'], row['port'], succeed_count))
        self._update_hidemyass(row['id'], kxflag)

    def do_hidemyass(self):
        sql = "update proxy_hidemyass set kxflag='bad' where kxflag='' and type <> 'HTTP' "
        self.db_conn.Execute(sql)

        if self.opt.full:
            sql = "select * from proxy_hidemyass where type='HTTP' "
        else:
            sql = "select * from proxy_hidemyass where type='HTTP' and length(kxflag) = 0"
        result_set = self.db_conn.QueryDict(sql)
        logging.info("sql: %s" % sql)
        logging.info("result_set len: %d" % len(result_set))

        for row in result_set:
            self.verify_hidemyass(row)

    def do_gen(self):
        sql = "select concat('http://', ip, ':', port) from proxy_hidemyass where kxflag in ('good', 'moderate') "
        result_set = self.db_conn.Query(sql)
        proxy_list = [i[0] for i in result_set]
        self.SaveList('proxy_list.txt', proxy_list)

    def run(self):
        if self.opt.gen:
            self.do_gen()
            sys.exit()

        self.do_hidemyass()


if __name__ == '__main__':
    btlog_init('log_verifier.log', logfile=True, console=True, level='DEBUG')
    v = ProxyVerifier()
    v.run()
