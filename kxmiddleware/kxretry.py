from scrapy import log
from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message

from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware

class KxRetryMiddleware(RetryMiddleware):

    def __init__(self, settings):
        RetryMiddleware.__init__(self, settings)

    def process_response(self, request, response, spider):
        log.msg('KxRetry process_response ===========')
        if 'dont_retry' in request.meta:
            return response

        if response.status != 200:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        log.msg('KxRetry process_exception ===============')
        return self._retry(request, exception, spider)
