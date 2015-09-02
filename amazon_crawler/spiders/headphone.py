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
from amazon_crawler.items import AmazonCatalogItem, AmazonDetailItem


class HeadphoneSpider(CrawlSpider):
    name = "headphone"
    allowed_domains = ["amazon.com"]
    start_urls = [
        'http://www.amazon.com/s?_encoding=UTF8&ie=UTF8&rh=n%3A172541%2Cp_n_feature_browse-bin%3A509312&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-3&pf_rd_r=0RHWRVH4HX5TMJCYT210&pf_rd_t=101&pf_rd_p=2187547522&pf_rd_i=172541']
    rules = (
        # Rule(LinkExtractor(allow=('page='), restrict_css=('.pagnLink')),
        # process_links="filter_links", callback='parse_catalog', follow=True),
        Rule(LinkExtractor(allow=('page='), restrict_css=('.pagnLink'))),
        Rule(LinkExtractor(restrict_css=('.s-access-detail-page')),
             callback='parse_detail')
    )
    REVIEW_COUNT_PATTERN = re.compile(r'[0-9]+,?[0-9]+')

    def _extract_review_count(self, s):
        return re.search(self.REVIEW_COUNT_PATTERN, s).group(0)

    def parse_reviews(self, response):
        self.logger.warning(response.url)
        self.logger.warning(response.meta['item_link'])

    def parse_detail(self, response):
        try:
            item = AmazonDetailItem()
            item['title'] = response.xpath(
                '//*[@id="productTitle"]/text()').extract_first()
            item['features'] = "\n".join(
                response.xpath('//*[@id="featurebullets_feature_div"]//span/text()').extract())

            review_count_string = response.xpath(
                '//*[@id="acrCustomerReviewText"]/text()').extract_first()
            item['review_count'] = self._extract_review_count(
                review_count_string)

            item['link'] = response.url
            item['review_link'] = response.xpath(
                '//*[@id="summaryStars"]/a/@href').extract_first()
            yield item
        except Exception as e:
            self.logger.error('parsing error: %s' % response)

        # 리뷰 크롤링
        yield Request(item['review_link'], meta={'item_link': item['link']}, callback=self.parse_reviews)

    def parse_catalog(self, response):
        item_containers = response.css('.s-item-container')
        for ic in item_containers:
            item = AmazonCatalogItem()
            try:
                item['title'] = ic.css(
                    'h2.s-access-title::text').extract_first()
                item['image_urls'] = ic.xpath('.//img/@src').extract()
                item['link'] = ic.css(
                    'a.s-access-detail-page').xpath('@href').extract_first()
                item['review_count'] = ic.xpath(
                    './/a[contains(@href, "#customerReviews")]/text()').extract_first()
                yield item
            except Exception as e:
                self.logger.error('parsing error: %s' % response)
                raise CloseSpider()
