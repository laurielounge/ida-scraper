import scrapy


class TestSpider(scrapy.Spider):
    name = 'test_spider'

    def __init__(self, api_identifier=None, audit_id=None, *args, **kwargs):
        super(TestSpider, self).__init__(*args, **kwargs)
        self.start_urls = [api_identifier]

    def start_requests(self):
        self.logger.info(f"Starting requests with start_urls: {self.start_urls}")
        for url in self.start_urls:
            self.logger.info(f"Making initial request to: {url}")
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Yielding the item for the current page
        self.logger.info(f"Parsing URL: {response.url}")
        self.logger.info(f"Response body: {response.body[:100]}")  # Log first 100 characters of body
        yield {
            'url': response.url,
            'status': response.status,
        }

        # Extracting and following internal links
        links = response.css('a::attr(href)').getall()
        self.logger.info(f"Found {len(links)} links on {response.url}")

        for link in links:
            # Ensure we're only following internal links
            if link.startswith('/'):
                link = response.urljoin(link)
            if self.is_internal_link(link):
                self.logger.info(f"Following internal link: {link}")
                yield scrapy.Request(url=link, callback=self.parse)

    def is_internal_link(self, url):
        # Ensure the URL belongs to the same domain
        return url.startswith(self.start_urls[0]) or url.startswith('/')
