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
from amazon_crawler.spiders import AmazonAbstractSpider

class ToySpider(AmazonAbstractSpider):
    name = "toy"
    allowed_domains = ["amazon.com"]
    start_urls = [
        'http://www.amazon.com/b/ref=s9_acss_bw_ct_Toys15Ca_ct1_cta?_encoding=UTF8&node=165993011&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-4&pf_rd_r=1BHFWKVM604JE677X59T&pf_rd_t=101&pf_rd_p=2151635282&pf_rd_i=165793011']
    
    def parse_detail(self, response):
        try:
            item = AmazonDetailItem()
            item['item_type'] = 'detail'
            item['title'] = response.xpath(
                '//*[@id="productTitle"]/text()').extract_first()
            item['features'] = " ".join(
                response.xpath('//*[@id="featurebullets_feature_div"]//span/text()').extract())

            item['review_count'] = self._extract_review_count(response)

            item['link'] = response.url
            item['review_link'] = response.xpath(
                '//*[@id="summaryStars"]/a/@href').extract_first()
            yield item
        except Exception as e:
            self.logger.error(e)
            self.logger.error('Failed to parse item_detail at %s' % response.url)
            
        # 리뷰 크롤링
        if item['review_link']:
            try:
                yield Request(item['review_link'], meta={'item_link': item['link']}, callback=self.parse_reviews)
            except Exception as e:
                self.logger.error(e)
                self.logger.error("Failed to follow review_link at %s" % response.url)