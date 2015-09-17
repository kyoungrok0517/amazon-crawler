# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider
from urlparse import parse_qsl, urlparse
from amazon_crawler.items import AmazonCatalogItem


class ToySpider(CrawlSpider):
    name = "toy"
    allowed_domains = ["amazon.com"]
    start_urls = [
        'http://www.amazon.com/b/ref=s9_acss_bw_ct_Toys15Ca_ct1_cta?_encoding=UTF8&node=165993011&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-4&pf_rd_r=1BHFWKVM604JE677X59T&pf_rd_t=101&pf_rd_p=2151635282&pf_rd_i=165793011']
    rules = (
        Rule(LinkExtractor(restrict_xpaths=('//a[@id="pagnNextLink"]')), callback='parse_catalog', follow=True),
    )

    def parse_catalog(self, response):   
        item_containers = response.xpath('//*[contains(@id, "result_")]')
        for ic in item_containers:
            item = AmazonCatalogItem()
            try:
                # item['title'] = ic.css(
                #     '.s-access-title::text').extract_first()
                # item['image_urls'] = ic.xpath('.//img/@src').extract()
                item['link'] = ic.xpath('(.//a/@href)[1]').extract_first()
                yield item
            except Exception as e:
                self.logger.error('parsing error: %s' % response)
                raise CloseSpider()

    def parse_detail(self, response):
        pass
