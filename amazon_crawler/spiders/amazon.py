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
            return [int(cnt.replace(',', '')) for cnt in re.findall(self.HELPFUL_VOTE_COUNT_PATTERN, s)]
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Error parsing helpful_vote_count at %s" % response.url)
            return None
    
    def parse_detail(self, response):
        raise NotImplementedError()
     
    def parse_reviews(self, response):
        review_containers = response.xpath(
            '//*[@id="cm_cr-review_list"]//div[@class="a-section review" and @id]')
        for rc in review_containers:
            item = AmazonReviewItem()
            item['item_type'] = 'review'
            try:
                link = rc.xpath('.//a[contains(@class, "review-title")]/@href').extract_first()
                item['link'] = response.urljoin(link)
                
                item['item_link'] = response.meta['item_link']
                item['helpful_vote_count'] = self._extract_helpful_vote_count(rc.xpath(
                    './/*[contains(@class, "helpful-votes-count")]//span/text()').extract_first())
                item['title'] = rc.xpath(
                    './/*[contains(@class, "review-title")]/text()').extract_first()
                item['text'] = " ".join(rc.xpath(
                    './/span[contains(@class, "review-text")]/text()').extract())

                if item['title']:
                    yield item

            except Exception as e:
                self.logger.error(e)
                self.logger.error('parsing error: %s' % response)