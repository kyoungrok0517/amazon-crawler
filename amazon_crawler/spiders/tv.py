# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider
from urlparse import parse_qsl, urlparse
from amazon_crawler.items import AmazonItem


class TvSpider(CrawlSpider):
    name = "tv"
    allowed_domains = ["amazon.com"]
    start_urls = [
        'http://www.amazon.com/b/ref=s9_acss_bw_ct_refTest_ct1_cta?_encoding=UTF8&node=172659&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-6&pf_rd_r=17SKVH9P8E9C5XCT9KDK&pf_rd_t=101&pf_rd_p=2174697142&pf_rd_i=1266092011']
    rules = (
        Rule(LinkExtractor(allow=('page='), restrict_xpaths=(
            '//div[@id="pagn"]')), callback='parse_catalog', follow=True),
    )

    def parse_catalog(self, response):
        item_containers = response.css('.s-item-container')
        for ic in item_containers:
            item = AmazonItem()
            try:
                item['title'] = ic.css(
                    '.s-access-title::text').extract_first()
                item['image_urls'] = ic.xpath('.//img/@src').extract()
                item['link'] = ic.css(
                    'a.s-access-detail-page').xpath('@href').extract_first()
                item['comments'] = ic.xpath(
                    './/a[contains(@href, "#customerReviews")]/text()').extract_first()
                yield item
            except Exception as e:
                self.logger.error('parsing error: %s' % response)
                raise CloseSpider()

    def parse_detail(self, response):
        pass
