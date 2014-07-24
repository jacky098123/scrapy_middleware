import os
import sys
import re
import pdb
import logging
import urllib
import urllib2
import cookielib
import time
import traceback
from optparse import OptionParser
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0


from scrapy.selector import HtmlXPathSelector
from bs4 import BeautifulSoup

sys.path.append('/home/yangrq/projects/pycore')
from utils.common_handler import CommonHandler
from utils.btlog import btlog_init
from db.mysqlv6 import MySQLOperator

from config import *


class ProxyDownloader(CommonHandler):
    RE = re.compile(".*\((.*?)\).*")
    def __init__(self,):
        self.crawled_proxys = []

        parser          = OptionParser()
        parser.add_option("--proxy", action="store", default="http://127.0.0.1:8087")
        parser.add_option("--try_times", action="store", default="10")
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

    '''
    ! IMPORTANT !
    change Cookie from firefox each time
    '''
    def _crawl_url(self, url):
        logging.info("_crawl_url ")
        content = ""
        request = urllib2.Request(
                url     = url,
                headers = {'Content-Type':'application/x-www-form-urlencoded','charset':'UTF-8',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0',
                        'Cookie': "hl=en; pv=26; userno=20140425-010621; from=direct; visited=2014%2F05%2F26+12%3A25%3A24; __utma=251962462.1210625505.1398409158.1400722703.1401074726.9; __utmz=251962462.1400037561.6.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __atuvc=4%7C18%2C12%7C19%2C6%7C20%2C3%7C21%2C2%7C22; __utmv=251962462.United%20States; __utmb=251962462.4.10.1401074726; __utmc=251962462",
                }
            )

        for i in range(int(self.opt.try_times)):
            try:
                o =urllib2.urlopen(request)
                if o.code / 100 == 2:
                    content = o.read()
            except Exception, e:
                logging.warn("e str: %s" % str(e))
            if len(content) > 2000:
                break
            time.sleep(1)

        if len(content) > 0:
            f = self._url2file(url)
            self.SaveFile(f, content)
            logging.info("save to %s" % f)
        return content

    def _selenium_crawl_url(self, url):
        logging.info("_selenium_crawl_url")
        content = ""
        profile = webdriver.FirefoxProfile()
        proxy = Proxy({'httpProxy': '127.0.0.1:8087'})
        profile.set_proxy(proxy)
        driver = webdriver.Firefox(profile)
        driver.get(url)
        try:
            element = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "fb-root")))
            content = driver.page_source
            content = content.encode('utf8', 'ignore')
        except Exception, e:
            logging.warn("exception: %s" % str(e))
        finally:
            driver.quit()

        if len(content) > 0:
            f = self._url2file(url)
            self.SaveFile(f, content)
            logging.info("save to %s" % f)
        return content

    def do_freeproxylists(self):
#        self._selenium_crawl_url('http://20140507.ip138.com/ic.asp')
        for idx in range(1,21):
#        for idx in (9,11):
            url = "http://www.freeproxylists.net/?pr=HTTP&page=%d" % (idx)
            logging.info("crawling: %s" % url)
            if self.opt.cache:
                content = self.LoadFile(self._url2file(url))
            else:
                content = self._selenium_crawl_url(url) # head has cookies
            self.parse(content)

    def parse(self, content):
        if len(content) == 0:
            logging.warn("content is empty")
            return

        hxs = HtmlXPathSelector(text=content)
        tr_selectors = hxs.select(".//*/table[@class='DataGrid']/tr")
        if len(tr_selectors) == 0:
            logging.warn("find data error")
            return

        # parse table
        head_flag = True
        for selector in tr_selectors:
            if head_flag:
                head_flag = False
                continue

            # parse row
            td_selectors = selector.select(".//td")
            print len(td_selectors)
            if len(td_selectors) != 10:
                logging.error("td_selectors is to short, parse row failed: %s" % str(td_selectors.select(".//text()").extract()))
                continue

            proxy_dict  = {'flag': 'failed'}
            td_idx      = 0
            for td_selector in td_selectors:
                if td_idx == 0:
                    ip_texts  = td_selector.select('.//script/text()').extract()
                    if len(ip_texts) > 0:
                        ip_contents = self.RE.findall(ip_texts[0])
                        if len(ip_contents) > 0:
                            proxy_dict['ip']    = urllib.unquote(ip_contents[0].strip("\""))
                elif td_idx == 1:
                    proxy_dict['port']      = td_selector.select('.//text()').extract()
                elif td_idx == 2:
                    proxy_dict['protocol']  = td_selector.select('.//text()').extract()
                elif td_idx == 3:
                    proxy_dict['anonymity'] = td_selector.select('.//text()').extract()
                elif td_idx == 4:
                    proxy_dict['country']   = td_selector.select('.//text()').extract()
                elif td_idx == 5:
                    proxy_dict['region']    = td_selector.select('.//text()').extract()
                elif td_idx == 6:
                    proxy_dict['city']      = td_selector.select('.//text()').extract()
                if td_idx >= 6:
                    proxy_dict['flag']  = 'succeed'
                    break
                td_idx += 1

            if proxy_dict['flag'] == 'succeed':
                proxy_dict.pop('flag')
                db_data             = {}
                for k,v in proxy_dict.iteritems():
                    if isinstance(v, list):
                        if len(v) > 0:
                            db_data[k] = v[0].strip()
                        else:
                            db_data[k] = ''
                    else:
                        db_data[k] = v

                db_data['create_time']  = datetime.now()
                db_data['kxflag']       = ''
                print db_data
                self.db_conn.Upsert('proxy_freeproxylists', db_data, ['ip','port'])

    def run(self):
        self.do_freeproxylists()

if __name__ == '__main__':
    btlog_init('log_download.log', logfile=True, console=True)
    d = ProxyDownloader()
    d.run()
