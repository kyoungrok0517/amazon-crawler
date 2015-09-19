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
    name = "book"
    allowed_domains = ["amazon.com"]
    start_urls = [
        'http://www.amazon.com/s/ref=lp_283155_nr_n_2?fst=as%3Aoff&rh=n%3A283155%2Cn%3A%211000%2Cn%3A3&bbn=1000&ie=UTF8&qid=1442667295&rnid=1000',
        'http://www.amazon.com/s/ref=lp_283155_nr_n_0?fst=as%3Aoff&rh=n%3A283155%2Cn%3A%211000%2Cn%3A1&bbn=1000&ie=UTF8&qid=1442667295&rnid=1000',
        'http://www.amazon.com/s/ref=lp_283155_nr_n_21?fst=as%3Aoff&rh=n%3A283155%2Cn%3A%211000%2Cn%3A3377866011&bbn=1000&ie=UTF8&qid=1442667295&rnid=1000']
    rules = (
        # Rule(LinkExtractor(restrict_xpaths=('//a[@id="pagnNextLink"]')), callback='parse_catalog', follow=True),
        Rule(LinkExtractor(restrict_xpaths=('//a[@id="pagnNextLink"]'))),
        Rule(LinkExtractor(restrict_css=('.s-access-detail-page')),
             callback='parse_detail')
    )
    
    def parse_detail(self, response):
        try:
            item = AmazonDetailItem()
            item['item_type'] = 'detail'
            item['title'] = response.xpath(
                '//*[@id="productTitle"]/text()').extract_first()
            # item['features'] = " ".join(
            #     response.xpath('//*[@id="featurebullets_feature_div"]//span/text()').extract())
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
     

