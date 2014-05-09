# Copyright (C) 2013 by Aivars Kalvans <aivars.kalvans@gmail.com>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import sys
import random
from scrapy import log

class KxRandomProxyMiddleware(object):
    def __init__(self, settings):
        PATH_NAME = os.path.dirname(__file__)
        proxy_file = os.path.join(PATH_NAME, 'proxy_list.txt')
        proxy_file = settings.get('PROXY_FILE', proxy_file)
        f = open(proxy_file)
        self.proxies = [l.strip() for l in f.readlines()]
        f.close()
        '''
        self.proxies = ['http://121.0.19.222:80',
                        'http://218.108.232.187:80',
                        'http://202.117.120.89:8080',]
        '''

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        log.msg('KxRandomProxy process_request ----------')
        proxy = random.choice(self.proxies)
        request.meta['proxy'] = proxy
        log.msg('KxRandomProxy using proxy: %s' % proxy)

        if len(self.proxies) == 0:
            log.msg('no proxy available', log.ERROR)
            sys.exit()

    def process_response(self, request, response, spider):
        log.msg('KxRandomProxy process_response ---------- <%d>' % response.status)
        if response.status != 200:
            proxy = request.meta['proxy']
            log.msg('KxRandomProxy response remove proxy <%s>, %d proxies left' % (proxy, len(self.proxies)-1))
#            try: self.proxies.remove(proxy)
#            except ValueError: pass
        return response

    def process_exception(self, request, exception, spider):
        log.msg('KxRandomProxy process_exception ----------')
        proxy = request.meta['proxy']
        log.msg('Removing failed proxy <%s>, %d proxies left' % (proxy, len(self.proxies)-1))
#        try: self.proxies.remove(proxy)
#        except ValueError: pass
