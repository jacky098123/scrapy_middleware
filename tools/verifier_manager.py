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
from multiprocessing import Process

from scrapy.selector import HtmlXPathSelector

sys.path.append('/home/yangrq/projects/pycore')
from utils.common_handler import CommonHandler
from utils.btlog import btlog_init
from utils.daemon_util import DaemonUtil
from db.mysqlv6 import MySQLOperator

from config import *
from proxy_verifier import ProxyVerifier

def do_verify(site, flag):
    print site, flag
    verifier = ProxyVerifier()
    if site == 'hidemyass':
        verifier.do_hidemyass(flag)
    elif site == 'freeproxylists':
        verifier.do_freeproxylists(flag)
    elif site == 'free_proxy_list':
        verifier.do_free_proxy_list(flag)
    else:
        raise Exception, 'invalid site'


class VerifierManager(CommonHandler,DaemonUtil):
    def __init__(self):
        DaemonUtil.__init__(self, 'verifier_manager')
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

    def run(self):
        if self.IsRunning('== running =='):
            return

        self.WritePidFile()

        process_pool = []
        for site in ('hidemyass', 'freeproxylists', 'free_proxy_list'):
            process_pool.append( Process(target=do_verify, args=(site, 'good')) )
            process_pool.append( Process(target=do_verify, args=(site, 'moderate')) )
            process_pool.append( Process(target=do_verify, args=(site, None)) )

        for process in process_pool:
            process.start()

        for process in process_pool:
            process.join()
            

if __name__ == '__main__':
    btlog_init('log_manager.log', logfile=True, console=True, level='DEBUG')
    v = VerifierManager()
    v.run()
