# /scraper_details/spiders/ida_spider.py
import re
from urllib.parse import urlparse, urldefrag

import scrapy
import tldextract
from scrapy import signals
from scrapy.signalmanager import dispatcher

from crud.scraper_cruds import clear_all_staging_data
from database.db_connections import DatabaseConnections
from scrapy_models.debug_items import ImageOnlyPage, AlreadyScannedPage, CanonicalPage
from scrapy_models.page import PageItem


class IDASpider(scrapy.Spider):
    name = 'ida_audit'

    def __init__(self, api_identifier=None, audit_id=None, *args, **kwargs):
        super(IDASpider, self).__init__(*args, **kwargs)
        self.logger.info(f"Starting the spider with API identifier: {api_identifier} and audit_id {audit_id}")
        self.page_id_counter = 0
        self.allowed_domains = []
        self.audit_id = audit_id  # Use the passed audit_id
        self.total_pages_discovered = set()  # Track unique URLs
        self.canonical_urls_set = set()  # Track canonical URLs

        # Add scheme if it's missing
        if not urlparse(api_identifier).scheme:
            api_identifier = 'https://' + api_identifier

        # Parse the domain and path separately
        parsed_start_url_parts = urlparse(api_identifier)
        self.logger.info(f"{parsed_start_url_parts=}")
        ext = tldextract.extract(api_identifier)
        base_domain = f"{ext.domain}.{ext.suffix}"  # e.g., "inghams.com.au" or "vushstimulation.com"
        subdomain = ext.subdomain  # e.g., "au" for "au.vushstimulation.com"

        # Handle the allowed domains, taking subdomains into account
        if subdomain:  # If there's a subdomain like "au" in "au.vushstimulation.com"
            self.allowed_domains = [f"{subdomain}.{base_domain}"]
        else:
            # Handle both the base domain and the www version if no subdomain exists
            self.allowed_domains = [base_domain, f"www.{base_domain}"]
        self.base_domain = parsed_start_url_parts.netloc.rstrip('/')  # Extract just the domain
        self.base_path = parsed_start_url_parts.path.rstrip('/')  # Extract just the path

        # Set base_path for internal link checking
        self.logger.info(f"Allowed domains set to: {self.allowed_domains}")
        self.logger.info(f"Base path set to: {self.base_path}")

        # Initialize database and session
        dba = DatabaseConnections()
        db = dba.get_audit_session()
        clear_all_staging_data(db=db, audit_id=self.audit_id)

        self.logger.info("We've completed the init and we're ready to start crawling")
        dispatcher.connect(self.handle_redirect, signal=signals.response_received)

    def start_requests(self):
        self.logger.info(f"Starting requests with start_urls: {self.start_urls}")
        for url in self.allowed_domains:
            # Check if the URL has a scheme; if not, add 'https://'
            if not urlparse(url).scheme:
                url = 'https://' + url
            self.logger.info(f"Making initial request to: {url}")
            yield scrapy.Request(url=url, callback=self.parse)

    def handle_redirect(self, response, request, spider):
        self.logger.info(f"Redirect detected from {request.url} to {response.url}")
        redirect_url = self.clean_url(response.url)
        parsed_redirect = urlparse(redirect_url)

        # Check if we are redirected from or to www and update allowed domains accordingly
        if parsed_redirect.netloc.replace('www.', '') in self.allowed_domains:
            if 'www.' in parsed_redirect.netloc:
                self.logger.info(f"Redirecting to www version: {redirect_url}")
                self.allowed_domains = [parsed_redirect.netloc, parsed_redirect.netloc.replace('www.', '')]
            else:
                self.logger.info(f"Redirecting to non-www version: {redirect_url}")
                self.allowed_domains = [parsed_redirect.netloc, 'www.' + parsed_redirect.netloc]

            self.logger.info(f"Updated allowed domains: {self.allowed_domains}")

        yield scrapy.Request(redirect_url, callback=self.parse)

    def parse(self, response):
        cleaned_body = re.sub(r'<noscript.*?</noscript>', '', response.text, flags=re.DOTALL)
        response = response.replace(body=cleaned_body.encode('utf-8'))
        requested_url = self.clean_url(response.url)  # This is the original URL
        self.logger.info(f"Processing requested URL: {requested_url}")

        # Check for image-only pages
        img_tags = response.css('body img')
        body_content = response.css('body *').getall()

        if len(img_tags) == 1 and len(body_content) == 1:
            self.logger.info(f"Skipping image-only page: {requested_url}")
            image_item = ImageOnlyPage(url=requested_url)
            yield image_item
            return

        # Handle canonical URLs
        canonical_url = response.xpath('//link[@rel="canonical"]/@href').get()
        alternate_urls = response.xpath('//link[@rel="alternate"]/@href').getall()

        if canonical_url:
            canonical_url = self.clean_url(canonical_url)
            self.logger.info(f"Found canonical URL: {canonical_url}")

            # Handle alternate URLs (hreflang)
            alternate_urls = [self.clean_url(url) for url in alternate_urls if url != canonical_url]
            alternate_urls.append(canonical_url)  # Add the canonical URL to the set of alternate URLs
            self.logger.info(f"Found alternate URLs: {alternate_urls}")
            canonical_item = CanonicalPage(url=requested_url, canonical_url=canonical_url, alternates=alternate_urls)
            yield canonical_item

        # If the requested URL was already processed, skip it
        if requested_url in self.total_pages_discovered:
            self.logger.info(f"Skipping already discovered page: {requested_url}")
            already_scanned_item = AlreadyScannedPage(url=requested_url)
            yield already_scanned_item
            return

        # Proceed with scraping
        self.page_id_counter += 1
        page_id = self.page_id_counter
        self.logger.info(f'Parsing requested URL: {requested_url} with page_id={page_id}')

        # Create and yield the page item
        page_item = self.create_page_item(response, page_id)
        yield page_item

        # Extract and follow links
        links = response.xpath('//a[@href]/@href').extract()
        internal_link_count = 0
        external_link_count = 0

        for link in links:
            if link.startswith('#') or not link.strip():
                continue
            full_url = response.urljoin(link)
            if self.is_internal_link(full_url) and not full_url.lower().endswith('.pdf'):
                internal_link_count += 1
                cleaned_url = self.clean_url(full_url)
                if cleaned_url not in self.total_pages_discovered:
                    yield scrapy.Request(cleaned_url, callback=self.parse)
            else:
                external_link_count += 1

        # Update internal and external link counts in the page item
        page_item['internal_link_count'] = internal_link_count
        page_item['external_link_count'] = external_link_count

        # After processing, mark the requested, canonical, and alternate URLs as discovered
        self.total_pages_discovered.add(requested_url)
        if canonical_url:
            self.total_pages_discovered.update(alternate_urls)
        self.logger.info(f"Marking these pages as discovered: {alternate_urls + [requested_url]}")

    def create_page_item(self, response, page_id):
        # Extract metadata from the page
        # print("Creating page item for URL: " + response.url)
        self.logger.info("Creating page item for URL: " + response.url)
        title = response.css('title::text').get()
        title_length = len(title) if title else 0
        crawl_depth = response.meta.get('depth', 0)
        h1_texts = response.css('h1::text').getall()
        h2_texts = response.css('h2::text').getall()
        h1_text = '\n'.join(h1_texts).strip() if h1_texts else ''
        h2_text = '\n'.join(h2_texts).strip() if h2_texts else ''
        h1_count = len(response.css('h1').getall())
        h2_count = len(response.css('h2').getall())
        image_link_count = len(response.css('img'))
        images_without_alt_count = len([img for img in response.css('img') if 'alt' not in img.attrib])

        page_item = PageItem(
            audit_id=self.audit_id,
            page_id=page_id,
            url=response.url,
            load_time=response.meta.get('download_latency'),
            title=title,
            title_length=title_length,
            crawl_depth=crawl_depth,
            h1=h1_text,
            h2=h2_text,
            h1_count=h1_count,
            h2_count=h2_count,
            image_link_count=image_link_count,
            images_without_alt_count=images_without_alt_count,
            status_code=response.status,
            meta_description=response.css('meta[name="description"]::attr(content)').get(),
            meta_description_length=len(response.css('meta[name="description"]::attr(content)').get() or ""),
            internal_link_count=0,
            external_link_count=0,
            has_meta_keywords=bool(response.css('meta[name="keywords"]::attr(content)').get()),
            is_https=urlparse(response.url).scheme == 'https',
            has_structured_data=bool(response.css('script[type="application/ld+json"]').get()),
            is_mobile_friendly=False
        )
        return page_item

    def is_internal_link(self, url):
        parsed_url = urlparse(url)

        # Check if the domain matches any of the allowed domains (www and non-www)
        domain_allowed = parsed_url.netloc in self.allowed_domains
        p_n = parsed_url.netloc in self.allowed_domains
        p_nl = parsed_url.netloc
        # Ensure the path starts with the same base path
        path_allowed = parsed_url.path.startswith(self.base_path)

        is_allowed = domain_allowed and path_allowed
        # print(f"url {url} {is_allowed=} {p_n=} {p_nl=} {self.allowed_domains=}")
        # self.logger.info(f"url {url} {is_allowed=} {p_n=} {p_nl=} {self.allowed_domains=}")
        self.logger.info(
            f"Checking internal link: {url} is_allowed={is_allowed} domain_allowed={domain_allowed} path_allowed={path_allowed}")

        return is_allowed

    def clean_url(self, url):
        # print("Cleaning URL: " + url)
        self.logger.info("Cleaning URL: " + url)
        parsed_url = urlparse(url)
        cleaned_url, _ = urldefrag(parsed_url._replace(fragment='').geturl())
        # Avoid stripping the trailing slash if the URL is just a domain (e.g., https://example.com/)
        if len(cleaned_url) > len(parsed_url.netloc) + len(parsed_url.scheme) + 3:
            cleaned_url = cleaned_url.rstrip('/')
        return cleaned_url

    def closed(self, reason):
        self.logger.info(f"Spider closed: {reason}")
        self.logger.info(f"Total processed pages: {self.page_id_counter}")
        print(f"Total discovered pages: {len(self.total_pages_discovered)}")
        # print(f"discovered pages: {self.total_pages_discovered}")
        self.logger.info(f"Total discovered pages: {len(self.total_pages_discovered)}")
