import os
import sys
import random
from scrapy import log

class KxRandomUserAgentMiddleware(object):
    def __init__(self, settings):
        PATH_NAME   = os.path.dirname(__file__)
        ua_file     = os.path.join(PATH_NAME, 'ua_list.txt')
        ua_file     = settings.get('USER_AGENT_FILE', ua_file)
        f = open(ua_file)
        self.useragents = [l.strip() for l in f.readlines()]
        f.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        useragent = random.choice(self.useragents)
        request.headers.setdefault('User-Agent', useragent)
