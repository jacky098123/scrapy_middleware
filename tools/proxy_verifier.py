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
        logging.info("ip: %s, port: %s, succeed_count: %d" % (ip, port, succeed_count))
        return kxflag

    def do_hidemyass(self):
        sql = "update proxy_hidemyass set kxflag='bad' where kxflag='' and type <> 'HTTP' "
        self.db_conn.Execute(sql)

        if self.opt.flag:
            sql = "select * from proxy_hidemyass where type='HTTP' and kxflag = '%s'" % self.opt.flag
        else:
            sql = "select * from proxy_hidemyass where type='HTTP' and length(kxflag) = 0"
        result_set = self.db_conn.QueryDict(sql)
        logging.info("sql: %s" % sql)
        logging.info("result_set len: %d" % len(result_set))

        for row in result_set:
            kxflag = self.real_verify(row['ip'], row['port'])
            sql = "update proxy_hidemyass set kxflag='%s' where id=%d" % (kxflag, row['id'])
            logging.info(sql)
            self.db_conn.Execute(sql)

    def do_free_proxy_list(self):
        sql = "update proxy_free_proxy_list set kxflag='bad' where kxflag='' and https='yes'"
        self.db_conn.Execute(sql)

        if self.opt.flag:
            sql = "select * from proxy_free_proxy_list where https='no' and kxflag = '%s'" % self.opt.flag
        else:
            sql = "select * from proxy_free_proxy_list where https='no' and length(kxflag) = 0"
        result_set = self.db_conn.QueryDict(sql)
        logging.info(sql)
        logging.info("result_set len: %d" % len(result_set))

        for row in result_set:
            kxflag = self.real_verify(row['ip'], row['port'])
            sql = "update proxy_free_proxy_list set kxflag='%s' where id=%d" % (kxflag, row['id'])
            logging.info(sql)
            self.db_conn.Execute(sql)

    def do_freeproxylists(self):
        if self.opt.flag:
            sql = "select * from proxy_freeproxylists where kxflag='%s'" % self.opt.flag
        else:
            sql = "select * from proxy_freeproxylists where length(kxflag) = 0"
        result_set = self.db_conn.QueryDict(sql)
        logging.info(sql)
        logging.info("result_set len: %d" % len(result_set))

        for row in result_set:
            kxflag = self.real_verify(row['ip'], row['port'])
            sql = "update proxy_freeproxylists set kxflag='%s' where id=%d" % (kxflag, row['id'])
            logging.info(sql)
            self.db_conn.Execute(sql)

    def gen(self):
        if not os.access('data', os.F_OK):
            os.mkdir('data')

        full_list   = []
        for kxflag in ('good', 'moderate'):
            # hidemyass
            sql = "select concat('http://', ip, ':', port) from proxy_hidemyass where kxflag = '%s'" % kxflag
            result_set = self.db_conn.Query(sql)
            logging.info(sql)
            logging.info("result_set len: %d" % len(result_set))
            proxy_list = [i[0] for i in result_set]

            # free_proxy_list
            sql = "select concat('http://', ip, ':', port) from proxy_free_proxy_list where kxflag = '%s'" % kxflag
            result_set = self.db_conn.Query(sql)
            logging.info(sql)
            logging.info("result_set len: %d" % len(result_set))
            for row in result_set:
                if row[0] not in proxy_list:
                    proxy_list.append(row[0])
            logging.info("final result_set len: %d" % len(proxy_list))

            # freeproxylists
            sql = "select concat('http://', ip, ':', port) from proxy_freeproxylists where kxflag = '%s'" % kxflag
            result_set = self.db_conn.Query(sql)
            logging.info(sql)
            logging.info("result_set len: %d" % len(result_set))
            for row in result_set:
                if row[0] not in proxy_list:
                    proxy_list.append(row[0])
            logging.info("final result_set len: %d" % len(proxy_list))

            file_name = 'data/proxy_list.%s.%s.txt' % (datetime.now().strftime('%Y-%m-%d'), kxflag)
            self.SaveList(file_name, proxy_list)
            full_list.extend(proxy_list)

        self.SaveList('data/proxy_list.%s.txt' % datetime.now().strftime('%Y-%m-%d'), full_list)
        self.SaveList('data/proxy_list.txt', full_list)

    def run(self):
        if self.opt.gen:
            self.gen()
            sys.exit()

        if self.opt.hidemyass:
            self.do_hidemyass()
        if self.opt.free_proxy_list:
            self.do_free_proxy_list()
        if self.opt.freeproxylists:
            self.do_freeproxylists()

if __name__ == '__main__':
    btlog_init('log_verifier.log', logfile=True, console=True, level='DEBUG')
    v = ProxyVerifier()
    v.run()
