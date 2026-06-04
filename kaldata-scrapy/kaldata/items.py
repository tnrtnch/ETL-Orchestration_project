import scrapy
from scrapy.item import Item, Field


class KaldataItem(scrapy.Item):
    title = scrapy.Field()
    pubdate = scrapy.Field()
    author = scrapy.Field()
    body = scrapy.Field()