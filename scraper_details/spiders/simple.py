import scrapy
from scrapy import signals
from scrapy.signalmanager import dispatcher


class TestSpider(scrapy.Spider):
    name = "test_spider"
    start_urls = ['https://www.mimeanalytics.com']

    def __init__(self, *args, **kwargs):
        super(TestSpider, self).__init__(*args, **kwargs)
        self.audit_id = 38
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_opened(self, spider):
        print(f"Spider {spider.name} opened")
        self.logger.info(f"Spider {spider.name} opened")

    def spider_closed(self, spider):
        print(f"Spider {spider.name} closed")
        self.logger.info(f"Spider {spider.name} closed")

    def start_requests(self):
        print(f"Starting requests from: {self.start_urls}")
        self.logger.info(f"Starting requests from: {self.start_urls}")
        for url in self.start_urls:
            self.logger.info(f"Generating request for: {url}")
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        print(f"Parsing URL: {response.url}")
        self.logger.info(f"Parsing URL: {response.url}")

        # Dummy item for testing
        yield {'url': response.url, 'audit_id': self.audit_id}
