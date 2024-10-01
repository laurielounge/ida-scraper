# /scraper_details/spiders/ida_spider.py
from urllib.parse import urlparse, urldefrag

import scrapy
from scrapy import signals
from scrapy.signalmanager import dispatcher

from crud.scraper_cruds import clear_all_staging_data
from database.db_connections import DatabaseConnections
from scraper_details.utils import remove_scheme
from scrapy_models.page import PageItem


class IdaSpider(scrapy.Spider):
    name = 'ida_audit'

    def __init__(self, api_identifier=None, audit_id=None, *args, **kwargs):
        super(IdaSpider, self).__init__(*args, **kwargs)
        self.start_urls = [api_identifier]
        self.logger.info(f"Starting the spider with API identifier: {api_identifier} and audit_id {audit_id}")
        dba = DatabaseConnections()
        db = dba.get_audit_session()
        self.page_id_counter = 0
        self.audit_id = audit_id
        clear_all_staging_data(db=db, audit_id=self.audit_id)

        cleaned_identifier = remove_scheme(api_identifier)
        parsed_start_url = urlparse(f"https://{cleaned_identifier}")

        base_domain = parsed_start_url.netloc.replace('www.', '').rstrip('/')
        www_domain = 'www.' + base_domain
        self.base_path = parsed_start_url.path.rstrip('/')
        self.allowed_domains = [base_domain, www_domain]
        self.logger.info(f"Allowed domains are: {self.allowed_domains} with base path: {self.base_path}")

        self.start_urls = [f'https://{base_domain}{self.base_path}', f'https://{www_domain}{self.base_path}']
        self.logger.info(f"Start URLs are: {self.start_urls}")

        dispatcher.connect(self.handle_redirect, signal=signals.response_received)
        self.master_set = set()  # To keep track of processed URLs

    def handle_redirect(self, response, request, spider):
        self.logger.info(f"Handling redirect from {request}")
        if response.status in [301, 302] and 'Location' in response.headers:
            location = response.headers['Location'].decode()
            redirect_domain = urlparse(location).netloc.rstrip('/')
            if redirect_domain and redirect_domain not in self.allowed_domains:
                self.allowed_domains.append(redirect_domain)
                self.logger.debug(f"Added redirected domain to allowed_domains: {redirect_domain}")

    def parse(self, response):
        cleaned_response_url = self.clean_url(response.url)
        print(f"Beginning parse: Cleaned response URL: {cleaned_response_url}")

        if cleaned_response_url in self.master_set:
            print(f"Beginning parse: Already parsed {cleaned_response_url} master set is {self.master_set}")
            self.logger.info(f"Skipping already processed URL: {response.url}")
            return

        self.master_set.add(cleaned_response_url)
        print(f"Master set after adding current URL: {self.master_set}")

        self.page_id_counter += 1
        page_id = self.page_id_counter
        self.logger.info(f'Parsing URL: {response.url} with page_id={page_id}')

        page_item = self.create_page_item(response, page_id)
        links = response.xpath('//a[@href]/@href').extract()
        internal_link_count = 0
        external_link_count = 0

        for link in links:
            print(f"Link: {page_id} {link}")
            if link.startswith('#') or not link.strip():
                print(f"Skipping link: {page_id} {link}")
                continue  # Skip anchor links and empty links

            full_url = response.urljoin(link)
            if self.is_internal_link(full_url):
                internal_link_count += 1
                cleaned_url = self.clean_url(full_url)
                if cleaned_url not in self.master_set:
                    # self.master_set.add(cleaned_url)
                    # print(f"Master set is now {self.master_set}")
                    self.logger.info(f"Creating request to follow link: {cleaned_url}")
                    yield scrapy.Request(cleaned_url, callback=self.parse)
            else:
                external_link_count += 1

        page_item['internal_link_count'] = internal_link_count
        page_item['external_link_count'] = external_link_count
        yield page_item

    def is_internal_link(self, url):
        parsed_url = urlparse(url)
        return parsed_url.netloc in self.allowed_domains and parsed_url.path.startswith(self.base_path)

    def clean_url(self, url):
        parsed_url = urlparse(url)
        cleaned_url, fragment = urldefrag(parsed_url._replace(fragment='').geturl())
        print(f"Cleaning url:{url=}, {parsed_url=}, {fragment=} cleaned = {cleaned_url.rstrip('/')}")
        return cleaned_url.rstrip('/')

    def create_page_item(self, response, page_id):
        content_type = response.headers.get('Content-Type', b'').decode('utf-8')
        if not content_type:
            content_type = 'unknown'

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
            internal_link_count=0,
            external_link_count=0,
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

        return page_item

    def closed(self, reason):
        self.logger.info(f"Spider closed: {reason}")
        self.logger.info(f"Processed URLs: {self.master_set}")
