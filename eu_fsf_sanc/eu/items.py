import scrapy


class EuItem(scrapy.Item):
    name = scrapy.Field()
    schema = scrapy.Field()
    sanctions = scrapy.Field()
    aliases = scrapy.Field()
