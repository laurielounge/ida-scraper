import scrapy


class PageLinkItem(scrapy.Item):
    # Define the fields for page link data
    audit_id = scrapy.Field()
    page_id = scrapy.Field()
    target_url = scrapy.Field()
    is_internal = scrapy.Field()
    anchor_text = scrapy.Field()
    mime_type = scrapy.Field()
    is_broken = scrapy.Field()
