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


class ToySpider(CrawlSpider):
    name = "toy"
    allowed_domains = ["amazon.com"]
    start_urls = [
        'http://www.amazon.com/b/ref=s9_acss_bw_ct_Toys15Ca_ct1_cta?_encoding=UTF8&node=165993011&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-4&pf_rd_r=1BHFWKVM604JE677X59T&pf_rd_t=101&pf_rd_p=2151635282&pf_rd_i=165793011']
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
        
    # def _extract_helpful_vote_count(self, s):
    #     try:
    #         return "%d/%d" % tuple(int(cnt.replace(',', '')) for cnt in re.findall(self.HELPFUL_VOTE_COUNT_PATTERN, s))
    #     except Exception as e:
    #         self.logger.error(e)
    #         self.logger.error(s)
    #         return None
    
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
        try:
            yield Request(item['review_link'], meta={'item_link': item['link']}, callback=self.parse_reviews)
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Failed to follow review_link at %s" % response.url)
     
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
                item['helpful_vote_count'] = rc.xpath(
                    './/*[contains(@class, "helpful-votes-count")]//span/text()').extract_first()
                item['title'] = rc.xpath(
                    './/*[contains(@class, "review-title")]/text()').extract_first()
                item['text'] = " ".join(rc.xpath(
                    './/span[contains(@class, "review-text")]/text()').extract())

                if item['title']:
                    yield item

            except Exception as e:
                self.logger.error(e)
                self.logger.error('parsing error: %s' % response)

    # def parse_catalog(self, response):   
    #     item_containers = response.xpath('//*[contains(@id, "result_")]')
    #     for ic in item_containers:
    #         item = AmazonCatalogItem()
    #         item['item_type'] = 'catalog'
    #         try:
    #             # item['title'] = ic.css(
    #             #     '.s-access-title::text').extract_first()
    #             # item['image_urls'] = ic.xpath('.//img/@src').extract()
    #             item['link'] = ic.xpath('(.//a/@href)[1]').extract_first()
    #             yield item
    #         except Exception as e:
    #             self.logger.error('parsing error: %s' % response)
    #             raise CloseSpider()

