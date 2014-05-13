# coding: utf8

import sys
import logging
import pdb
import urllib
import random

sys.path.append("/home/yangrq/projects/pycore")

from utils.common_handler import CommonHandler
from utils.http_client import HttpClient

from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.spider import BaseSpider


class BaiduCommon(CommonHandler, HttpClient):
    TEST_FILE   = "html_baidu.html"
    KEYWORD_LIST = [
        '长沙机票',
        '长春机票',
        '重庆机票',
        '鄂尔多斯机票',
        '邯郸机票',
        '运城机票',
        '赣州机票',
        '贵阳机票',
        '西安机票',
        '西宁机票',
        '石家庄机票',
        '珠海机票',
        '烟台机票',
        '温州机票',
        '深圳机票',
        '济南机票',
        '沈阳机票',
        '汕头机票',
        '榆林机票',
        '桂林机票',
        '杭州机票',
        '昆明机票',
        '无锡机票',
        '拉萨机票',
        '成都机票',
        '徐州机票',
        '张家界机票',
        '延吉机票',
        '广州机票',
        '常州机票',
        '宜昌机票',
        '宁波机票',
        '威海机票',
        '太原机票',
        '大庆机票',
        '呼和浩特机票',
        '合肥机票',
        '厦门机票',
        '南昌机票',
        '南京机票',
        '北海机票',
        '北京机票',
        '包头机票',
        '兰州机票',
        '佳木斯机票',
        '九寨沟机票',
        '乌鲁木齐机票',
        '义乌机票',
        '丽江机票',
        '上海机票',]


    @staticmethod
    def parse(html):
        parse_dict  = {}
        hxs = HtmlXPathSelector(text=html)

        content_left_selectors = hxs.select(".//*[@id='content_left']")
        if len(content_left_selectors) > 0:
            parse_dict['valid_flag'] = 1
        else:
            parse_dict['valid_flag'] = 0
            return parse_dict

        # parse sem content
        sem_selectors = hxs.select(".//*[@id='content_left']/table[contains(@class,'EC_mr15')]")
        parse_dict['sem_count']         = len(sem_selectors) / 2

        # parse ALADING and SEO
        result_selectors = hxs.select(".//*[@id='content_left']/div[starts-with(@class,'result')]")
        if len(result_selectors) > 0:
            idx = 1
            for result_selector in result_selectors:
                result_class = result_selector.select("@class").extract()
                if len(result_class) > 0:
                    result_class = result_class[0]
                    if result_class.startswith('result-op'):
                        if not parse_dict.has_key('ding_flag'): # ALADING already set alading
                            parse_dict['ding_flag']     = 1
                            parse_dict['ding_pos']      = idx
                    elif result_class.startswith('result c-container'): # SEO
                        domain_list = result_selector.select(".//div/span[@class='g']/text()").extract()
                        if len(domain_list) > 0:
                            domain = domain_list[0].lower()
                            domain = domain.split('/')[0]
                            if domain.find('kuxun.') >= 0:
                                if not parse_dict.has_key('kuxun_rank'):
                                    parse_dict['kuxun_rank'] = idx
                            elif domain.find('ctrip.') >= 0:
                                if not parse_dict.has_key('ctrip_rank'):
                                    parse_dict['ctrip_rank'] = idx
                            elif domain.find('qunar.') >= 0:
                                if not parse_dict.has_key('qunar_rank'):
                                    parse_dict['qunar_rank'] = idx
                            elif domain.find('17u.') >= 0:
                                if not parse_dict.has_key('17u_rank'):
                                    parse_dict['17u_rank']  = idx
                            elif domain.find('daodao.') >= 0:
                                if not parse_dict.has_key('daodao_rank'):
                                    parse_dict['daodao_rank'] = idx
                            elif domain.find('elong.') >= 0:
                                if not parse_dict.has_key('elong_rank'):
                                    parse_dict['elong_rank'] = idx
                            elif domain.find('zhuna.') >= 0:
                                if not parse_dict.has_key('zhuna_rank'):
                                    parse_dict['zhuna_rank'] = idx
                idx += 1
        return parse_dict

    @staticmethod
    def random_request():
#        url = "http://www.baidu.com/baidu?wd=%E9%87%8D%E5%BA%86%E6%9C%BA%E7%A5%A8&ie=utf-8&usm=1&rn=100"
#        url = "http://www.baidu.com/s?ie=utf-8&mod=0&isid=F3B6D39EEF328045&pstg=0&wd=%E9%87%8D%E5%BA%86%E6%9C%BA%E7%A5%A8&ie=utf-8&tn=baiduhome_pg&f=8&bs=%E9%87%8D%E5%BA%86%E6%9C%BA%E7%A5%A8&rsv_bp=1&rsv_spt=1&inputT=0&rsv_sid=1463_5451_5223_4261_4759_5516&f4s=1&_cr1=15995&rn=100"

        keyword = random.choice(BaiduCommon.KEYWORD_LIST)
        url = "http://www.baidu.com/s?ie=utf-8&mod=0&isid=F3B6D39EEF328045&pstg=0&wd=%s&ie=utf-8&tn=baiduhome_pg&f=8&rn=100" % urllib.quote_plus(keyword)
        return url

    def test_parse(self, p=False):
        html_data = self.LoadFile(self.TEST_FILE)
        data_dict   = BaiduCommon.parse(html_data)
        if p:
            for k,v in data_dict.iteritems():
                print k, v

    def fetch_file(self):
        url = BaiduCommon.random_request()
        urllib.urlretrieve(url, self.TEST_FILE)

if __name__ == '__main__':
    b   = BaiduCommon()
    b.fetch_file()
    b.test_parse(True)
