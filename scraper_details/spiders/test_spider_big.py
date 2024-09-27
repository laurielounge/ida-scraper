from urllib.parse import urlparse, urljoin

import scrapy
from scrapy import signals
from scrapy.signalmanager import dispatcher

from scrapy_models.page import PageItem  # Ensure these imports are correct


class TestSpiderBig(scrapy.Spider):
    name = "test_spider_big"
    start_urls = ['https://www.mimeanalytics.com']

    def __init__(self, *args, **kwargs):
        super(TestSpiderBig, self).__init__(*args, **kwargs)
        self.audit_id = 38
        self.page_id_counter = 1
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_opened(self, spider):
        self.logger.info(f"Spider {spider.name} opened")

    def spider_closed(self, spider):
        self.logger.info(f"Spider {spider.name} closed")

    def start_requests(self):
        self.logger.info(f"Starting requests from: {self.start_urls}")
        for url in self.start_urls:
            self.logger.info(f"Generating request for: {url}")
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, meta=None):
        page_id = self.page_id_counter
        self.logger.info(f'Parsing unique URL {response.url} with page_id={page_id}')
        self.page_id_counter += 1
        internal_link_count = 0
        external_link_count = 0
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')

        if not content_type:
            self.logger.warning(f'Content-Type header is missing for {response.url}')
            content_type = 'unknown'

        try:
            current_domain = urlparse(response.url).netloc.rstrip('/')
            all_links = response.css('a')
            link_text_list = []
            valid_links = set()  # Use a set to avoid duplicates

            for link in all_links:
                url = link.attrib.get('href')
                text = link.css('::text').get() or link.get()
                link_text_list.append(f"{text}: {url}")
                if url and url != '/':
                    if url.startswith('#') or url.startswith('tel:'):
                        continue  # Skip anchors and phone links
                    normalized_url = urljoin(response.url, url).rstrip('/')
                    if self.is_internal_link(normalized_url, current_domain):
                        internal_link_count += 1
                    else:
                        external_link_count += 1
                    valid_links.add(normalized_url)

            title = response.css('title::text').get()
            title_length = len(title) if title else 0
            crawl_depth = response.meta.get('depth', 0)
            h1_texts = response.css('h1::text').getall()
            h2_texts = response.css('h2::text').getall()
            h1_text = '\n'.join(h1_texts).strip() if h1_texts else ''
            h2_text = '\n'.join(h2_texts).strip() if h2_texts else ''
            self.logger.info(f"h1 and h2 values: {h1_texts=} and {h2_texts=}")
            h1_count = len(response.css('h1').getall())
            h2_count = len(response.css('h2').getall())

            images = response.css('img')
            image_link_count = len(images)
            images_without_alt_count = len([img for img in images if not img.attrib.get('alt')])

            page_links = response.css('a::attr(href)').getall()
            page_link_count = len(page_links)

            meta_description = response.css('meta[name="description"]::attr(content)').get()
            meta_description_length = len(meta_description) if meta_description else 0
            is_https = urlparse(response.url).scheme == 'https'

            has_meta_keywords = bool(response.css('meta[name="keywords"]::attr(content)').get())
            is_mobile_friendly = False  # Placeholder, actual implementation may vary
            has_structured_data = bool(response.css('script[type="application/ld+json"]').get())
            duplicate_content_flag = False  # Placeholder, actual implementation needed
            broken_link_count = 0  # Implement logic to check for broken links

            self.logger.info(f'Yielding PageItem for URL {response.url}')

            page_item = PageItem(
                audit_id=self.audit_id,
                page_id=page_id,
                url=response.url,
                load_time=response.meta.get('download_latency'),
                content_type=content_type,
                title=title,
                title_length=title_length,
                crawl_depth=crawl_depth,
                h1=h1_text,
                h2=h2_text,
                h1_count=h1_count,
                h2_count=h2_count,
                page_link_count=page_link_count,
                image_link_count=image_link_count,
                internal_link_count=internal_link_count,
                external_link_count=external_link_count,
                images_without_alt_count=images_without_alt_count,
                status_code=response.status,
                meta_description_length=meta_description_length,
                has_meta_keywords=has_meta_keywords,
                is_mobile_friendly=is_mobile_friendly,
                has_structured_data=has_structured_data,
                is_https=is_https,
                duplicate_content_flag=duplicate_content_flag,
                broken_link_count=broken_link_count,
                meta_description=meta_description
            )
            print(f"About to yield PageItem: {page_item}")
            self.logger.info(f"Yielding PageItem: {page_item}")
            yield page_item

            self.logger.info(f'Found {len(valid_links)} valid links on page {response.url}')
        except Exception as e:
            print(f'Error parsing URL {response.url}: {e}')
            self.logger.error(f'Error parsing URL {response.url}: {e}')

    @staticmethod
    def is_internal_link(url, domain):
        return urlparse(url).netloc == domain
