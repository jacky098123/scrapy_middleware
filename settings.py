

# add this to you setting.py
RETRY_TIMES         = 15
COOKIES_ENABLED     = False
DOWNLOAD_DELAY      = 2
DOWNLOAD_TIMEOUT    = 10

#USER_AGENT_FILE = ''
#PROXY_FILE = ''

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': None, # disable it

	'scrapy.kxmiddleware.kxretry.KxRetryMiddleware': 90, # FIXME
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': None, # disable it

	'scrapy.kxmiddleware.kxrandom_useragent.KxRandomUserAgentMiddleware': 91, # FIXME
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None, # disable it

	'scrapy.kxmiddleware.kxrandom_proxy.KxRandomProxyMiddleware': 100, # FIXME
	'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': None, # disable it
}
