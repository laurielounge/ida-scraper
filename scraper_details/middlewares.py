# scraper_details/middlewares.py
import random
import traceback

from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException  # Add WebDriverException for more coverage
from selenium.webdriver.chrome.service import Service

from logging_mod.logger import logger

logger.debug("Opening middlewares file.")

# List of user agents to rotate
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.18363 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/88.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.2; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; SAMSUNG SM-N950U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/87.0.664.66 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/86.0.622.69 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
]


class SeleniumMiddleware:
    def __init__(self):
        # Initialize the Selenium WebDriver
        self.driver = self.start_driver()

    def start_driver(self):
        options = webdriver.ChromeOptions()
        for arg in [
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            '--disable-extensions',
            '--enable-logging',
            '--v=1'
        ]:
            options.add_argument(arg)

        # Use a Chrome service to start the driver, logging ChromeDriver actions
        chrome_service = Service(executable_path='/usr/local/bin/chromedriver')  # Specify path to ChromeDriver
        chrome_service.log_path = '/opt/scraper_service/logs/chrome_output.log'  # Log to a specific file

        logger.info("Starting Chrome WebDriver with Selenium")

        driver = webdriver.Chrome(service=chrome_service, options=options)
        driver.set_page_load_timeout(60)

        logger.info("Chrome WebDriver started successfully.")
        return driver

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to instantiate the middleware
        middleware = cls()
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def process_request(self, request, spider):
        spider.logger.info("PROCESSED REQUEST This is coming from spider.logger")
        logger.info("PROCESSED REQUEST This is coming from custom logger")

        if 'cached' in request.meta:
            logger.info(f"Skipping Selenium for cached request: {request.url}")
            spider.logger.info(f"SPIDER LOGGER Skipping Selenium for cached request: {request.url}")
            return None

        logger.info(f"Using Selenium for request: {request.url}")
        spider.logger.info(f"SPIDER LOGGER Using Selenium for request: {request.url}")
        try:
            self.driver.get(request.url)
            body = str.encode(self.driver.page_source)
            return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)
        except TimeoutException:
            logger.error(f"Timeout processing request for URL: {request.url}")
            logger.error(f"Failed to process page: {request.url} due to timeout.")
            return HtmlResponse(request.url, status=504, body=b"Timeout exceeded")
        except WebDriverException as e:
            logger.error(f"WebDriverException on {request.url}: {str(e)}")
            logger.error(f"Failed to process page: {request.url} due to WebDriverException.")
            self.restart_driver(spider, request)  # Restart driver and retry request
            return self._retry_request(request)
        except Exception as e:
            logger.error(f"Unknown error on {request.url}: {str(e)}")
            logger.error(f"Failed to process page: {request.url} due to unknown error.")
            logger.error(traceback.format_exc())
            return HtmlResponse(request.url, status=500, body=str(e).encode('utf-8'))

    def restart_driver(self, spider, request):
        logger.info(f"Restarting Selenium WebDriver due to a crash on {request.url}.")
        try:
            self.driver.quit()  # Quit the current driver session
        except Exception as e:
            logger.error(f"Error quitting driver on {request.url}: {e}")
        self.driver = self.start_driver()  # Restart the driver

    def _retry_request(self, request):
        retry_request = request.copy()
        retry_request.dont_filter = True  # Ensure retry request isn't filtered as a duplicate
        return retry_request

    def spider_closed(self, spider):
        logger.info("Closing Selenium WebDriver.")
        self.driver.quit()


class CustomMiddleware:
    def __init__(self):
        pass

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        logger.info('Spider opened: %s' % spider.name)

    def process_request(self, request, spider):
        # Set a random User-Agent
        request.headers['User-Agent'] = random.choice(USER_AGENTS)
        request.headers['Accept-Language'] = 'en-US,en;q=0.9'
        # Continue processing this request
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request() (from other downloader middleware) raises an exception.
        pass


class LoggingMiddleware:
    def process_response(self, request, response, spider):
        logger.info(f"Visited {response.url}")
        return response


class ErrorHandlingMiddleware:
    def process_response(self, request, response, spider):
        logger.info(f"Handling error for request: {request.url}")
        if response.status != 200:
            # Handle non-OK responses
            raise IgnoreRequest
        return response
