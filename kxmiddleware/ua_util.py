#!/usr/bin/python
# encoding: utf8

import os
import sys
import time
import logging
import urllib
import pdb
import traceback
from optparse import OptionParser
from datetime import datetime
from bs4 import BeautifulSoup

sys.path.append("/home/yangrq/projects/pycore")

from utils.common_handler import CommonHandler
from utils.btlog import btlog_init

class UAUtil(CommonHandler):
    def _crawl_url(self, url):
        try:
            html_data = urllib.urlopen(url).read()
        except Exception, e:
            logging.warn("e: %s" % str(e))
            logging.warn("traceback: %s" % traceback.print_exc())
            return ""
        return html_data

    def _parse_html(self, html_data):
        logging.info("html_data len: %d" % len(html_data))
        ua_list = []
        try:
            soup = BeautifulSoup(html_data, from_encoding='utf-8')
            li_list = soup.find_all('li')
            for li in li_list:
                a_text = li.find('a').text
                ua_list.append(a_text.strip())
        except Exception, e:
            logging.warn("e: %s" % str(e))
            logging.warn("traceback: %s" % traceback.print_exc())
            return ua_list
        return ua_list

    def do_url(self, url):
        logging.debug("url: %s" % self.ToString(url))
        html_data = self._crawl_url(url)
        if len(html_data) == 0:
            return
        return self._parse_html(html_data)

    def run(self):
        url_list = [
            "http://www.useragentstring.com/pages/Chrome/",
            "http://www.useragentstring.com/pages/Internet%20Explorer/",
            "http://www.useragentstring.com/pages/Firefox/",
        ]
        total_ua_list = []
        for url in url_list:
            a_list = self.do_url(url)
            total_ua_list.extend(a_list)

        self.SaveList('ua_list.txt', total_ua_list)

if __name__ == '__main__':
    btlog_init("log_kuoci_processor.log", logfile=False, console=True, level='DEBUG')
    p = UAUtil()
    p.run()
