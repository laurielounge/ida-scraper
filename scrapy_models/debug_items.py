# debug_items.py
from scrapy import Item, Field


class ImageOnlyPage(Item):
    url = Field()


class AlreadyScannedPage(Item):
    url = Field()


class CanonicalPage(Item):
    url = Field()
    canonical_url = Field()
    alternates = Field()