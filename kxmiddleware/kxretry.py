# coding: utf8
from scrapy import log
from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message

from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware

'''
有些页面抓取的结果始终是 404, 301 等
如果采用scapy内部的参数: RETRY_TIMES 来处理，这样的页面始终无法到达应用层的spider， spider 无法相应的任务进行处理
必须添加机制保证任务仍然到达 spider，由spider 来决定如何处理这样的任务
'''

class KxRetryMiddleware(RetryMiddleware):

    def __init__(self, settings):
        RetryMiddleware.__init__(self, settings)

    def process_response(self, request, response, spider):
        log.msg('KxRetry process_response ===========')
        if 'dont_retry' in request.meta:
            return response

        if response.status != 200:
            if 'retry_middleware' in request.meta:
                request.meta['retry_middleware'] += 1
            else:
                request.meta['retry_middleware'] = 1
            if request.meta['retry_middleware'] > 4:
                response.status = 200
                return response

            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        log.msg('KxRetry process_exception ===============')
        return self._retry(request, exception, spider)
