import os
import sys
import logging
import urllib2
import time
import traceback
from datetime import datetime

from scrapy.selector import HtmlXPathSelector

sys.path.append('/home/yangrq/projects/pycore')
from utils.common_handler import CommonHandler
from utils.btlog import btlog_init
from db.mysqlv6 import MySQLOperator

from baidu_common import BaiduCommon
from config import *

class Tool(CommonHandler):
    def __init__(self):
        self.db_conn = MySQLOperator()
        if not self.db_conn.Connect(**DB_CONF):
            raise Exception, "db error"

    def run(self):
        for flag in ('good', 'moderate', ''):
            for table in ('proxy_free_proxy_list', 'proxy_freeproxylists', 'proxy_hidemyass'):
                sql = "select count(*) from %s where kxflag = '%s' " % (table, flag)
                result_set = self.db_conn.Query(sql)
                logging.info(sql)
                logging.info("count: %d" % result_set[0][0])

if __name__ == '__main__':
    btlog_init(logfile=False, console=True, level='DEBUG')
    v = Tool()
    v.run()
