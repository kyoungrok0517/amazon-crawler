# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider
from urlparse import parse_qsl, urlparse


class HeadphoneSpider(CrawlSpider):
    name = "headphone"
    allowed_domains = ["amazon.com"]
    start_urls = [
        'http://www.amazon.com/s?_encoding=UTF8&ie=UTF8&rh=n%3A172541%2Cp_n_feature_browse-bin%3A509312&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-3&pf_rd_r=0RHWRVH4HX5TMJCYT210&pf_rd_t=101&pf_rd_p=2187547522&pf_rd_i=172541']
    rules = (
        Rule(LinkExtractor(allow=('page='), restrict_css=('.pagnLink')),
             process_links="filter_links"),
        Rule(LinkExtractor(restrict_css=('.s-access-detail-page')),
             callback='parse_detail')
    )

    def filter_links(self, links):
        # for link in links:
        #     self.logger.warning(link.url)
        return links

    # def start_requests(self):
    #     pass

    def parse_detail(self, response):
        self.logger.warning(response.url)
