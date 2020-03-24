# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HaikuWriterItem(scrapy.Item):
    timestamp = scrapy.Field()
    text = scrapy.Field()
    author = scrapy.Field()
    body_text = scrapy.Field()
    url = scrapy.Field()
    subreddit = scrapy.Field()
