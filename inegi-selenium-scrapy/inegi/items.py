import scrapy

class InegiItem(scrapy.Item):
    name = scrapy.Field()
    sanction_numbers = scrapy.Field()
    origin = scrapy.Field()

