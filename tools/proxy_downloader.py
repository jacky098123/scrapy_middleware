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

DB_CONF = {
    "host"  : "192.168.0.57",
    "user"  : "product_w",
    "passwd": "kooxootest",
    "database"  : "proxy",
    "port"      : 3306,
    "charset"   : "utf8"
}

'''
drop table if exists proxy_hidemyass;
create table proxy_hidemyass (
id int auto_increment,
ip varchar(64) default '',
port varchar(16) default '',
country varchar(64) default '',
type varchar(16) default '',
anonymity varchar(32) default '',
kxflag varchar(16) default '' comment 'good,moderate,pool,bad',
create_time timestamp default '0000-00-00 00:00:00',
update_time timestamp default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
primary key(id),
key idx_u(ip, port)
) engine=InnoDb, charset='utf8';

'''

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


    def _parse_hidemyass(self, html_data):
        def parse_style(html):
            style_str = html.split("</style>")[0]
            items = style_str.split('.')
            kv_dict = {}
            for item in items:
                if item.find('{') < 0:
                    continue
                kv = item.split('{')
                kv_dict[kv[0]] = kv[1].strip().strip('}')
            return kv_dict

        def extract_text(tag):
            text = re.findall(r'<.*?>(.*?)</.*?>', tag)
            return text[0]

        def process_tag(html):
            # process <span/> # TODO

            # process <span> </span>
            spanlist = re.findall(r'<.*?</\w+>', html)

            text_list = []
            for span in spanlist:
                if re.findall(r'display:\s*none', span):
                    html = html.replace(span, '')
                    continue
                html = html.replace(span, extract_text(span))
            return html

        logging.info("parse html_data len: %d" % len(html_data))

        selector = HtmlXPathSelector(text=html_data)
        tr_selector_list = selector.select('//table[@id="listtable"]/tr')

        proxy_list = []
        for tr_selector in tr_selector_list:
            proxy_dict = {}
            proxy_dict['ip']        = tr_selector.select('.//td[2]/span').extract()[0]
            proxy_dict['port']      = tr_selector.select('.//td[3]/text()').extract()[0]
            proxy_dict['country']   = tr_selector.select('.//td[4]/span/text()').extract()[0]
            proxy_dict['type']      = tr_selector.select('.//td[7]/text()').extract()[0]
            proxy_dict['anonymity'] = tr_selector.select('.//td[8]/text()').extract()[0]

            kv_dict = parse_style(proxy_dict['ip'])
            content_str = proxy_dict['ip'].split("</style>")[1]
            content_str = content_str.strip()[:-7] # strip the end </span>
            for k,v in kv_dict.iteritems():
                content_str = content_str.replace(k,v)
            proxy_dict['ip']        = process_tag(content_str)

            for k,v in proxy_dict.iteritems():
                proxy_dict[k] = v.strip()
            proxy_list.append(proxy_dict)

        return proxy_list

    def do_url(self, url, callback):
        logging.info("do url: %s" % url)
        html_data = ""
        if self.opt.cache:
            file_name = self._url2file(url)
            if os.access(file_name, os.F_OK):
                html_data = self.LoadFile(file_name)
        if len(html_data) == 0:
            html_data = self._crawl_url(url)

        if html_data <= 100:
            logging.warn("html_data length too short: %d" % len(html_data))
            return

        try:
            proxy_list = callback(html_data)
        except Exception, e:
            logging.warn("error: %s" % str(e))
            logging.warn("traceback is: %s" % traceback.print_exc())
            return []

        logging.info("callback return proxy_list len: %d" % len(proxy_list))
        return proxy_list

    def do_hidemyass(self):
        url_list = [
            "http://hidemyass.com/proxy-list/1",
            "http://hidemyass.com/proxy-list/2",
        ]
        for url in url_list:
            proxy_list = self.do_url(url, self._parse_hidemyass)
            for proxy in proxy_list:
                print proxy
                proxy['create_time'] = datetime.now()
                self.db_conn.Upsert('proxy_hidemyass', proxy, ['ip', 'port'])

    def do_proxy_org(self):
        pass

    def _baidu_callback(self, html_data):
        logging.info("baidu callback len: %d" % len(html_data))
        return []

    def do_baidu(self):
        self.do_url('http://www.baidu.com/', self._baidu_callback)

    def run(self):
        self.do_hidemyass()
        self.do_proxy_org()

if __name__ == '__main__':
    btlog_init('log_download.log', logfile=True, console=True)
    d = ProxyDownloader()
    d.run()
