# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ThreadItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    page = scrapy.Field()
    title = scrapy.Field()
    posts = scrapy.Field()

class PostItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    screen_name = scrapy.Field()
    user_name = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    top = scrapy.Field()
    contents = scrapy.Field()

