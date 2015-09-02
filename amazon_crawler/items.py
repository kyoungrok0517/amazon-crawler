# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonCatalogItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    review_count = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()


class AmazonDetailItem(scrapy.Item):
    title = scrapy.Field()
    features = scrapy.Field()
    review_count = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
    link = scrapy.Field()
    review_link = scrapy.Field()


class AmazonReviewItem(scrapy.Item):
    helpful_vote_count = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    item_link = scrapy.Field()
