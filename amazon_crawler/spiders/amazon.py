# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import scrapy
import re
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider
from urlparse import parse_qsl, urlparse
from amazon_crawler.items import AmazonCatalogItem, AmazonDetailItem, AmazonReviewItem


class AmazonAbstractSpider(CrawlSpider):
    name = "_amazon"
    allowed_domains = ["amazon.com"]
    start_urls = []
    rules = (
        # Rule(LinkExtractor(restrict_xpaths=('//a[@id="pagnNextLink"]')), callback='parse_catalog', follow=True),
        Rule(LinkExtractor(restrict_xpaths=('//a[@id="pagnNextLink"]'))),
        Rule(LinkExtractor(restrict_css=('.s-access-detail-page')),
             callback='parse_detail')
    )
    
    REVIEW_COUNT_PATTERN = re.compile(r'[0-9]+(,?[0-9]*)')
    HELPFUL_VOTE_COUNT_PATTERN = re.compile(r'[0-9,]+')
    def _extract_review_count(self, response):
        try:
            s = response.xpath('//*[@id="acrCustomerReviewText"]/text()').extract_first()
            count_string = str(re.search(self.REVIEW_COUNT_PATTERN, s).group(0)) 
            return int(count_string.replace(',', ''))
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Error parsing review_count at %s" % response.url)
            return None
        
    def _extract_helpful_vote_count(self, s):
        try:
            return tuple(int(cnt.replace(',', '')) for cnt in re.findall(self.HELPFUL_VOTE_COUNT_PATTERN, s))
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Error parsing helpful_vote_count at %s" % response.url)
            return None
    
    def parse_detail(self, response):
        raise NotImplementedError()
     
    def parse_reviews(self, response):
        raise NotImplementedError()