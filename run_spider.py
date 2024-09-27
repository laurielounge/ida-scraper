#!/opt/scraper_venv/bin/python
from multiprocessing import Process

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scraper.spiders.ida import IdaSpider


def run_spider_batch(domain_list):
    process = CrawlerProcess(get_project_settings())
    for domain in domain_list:
        process.crawl(IdaSpider, domain=domain)
    process.start()


# run_spider.py
def run_spider():
    process = CrawlerProcess(get_project_settings())
    domain_list = ['www.mimeanalytics.com', 'independentdigitalaudit.com.au', 'feelsbotanical.com.au', 'inghams.com.au',
                   'themeatandwineco.com', 'hunterandbarrel.com/au/', 'ribsandburgers.com/au/']

    domain_list = ['www.mimeanalytics.com', 'independentdigitalaudit.com.au', 'feelsbotanical.com.au', 'inghams.com.au',
                   ]
    domain_list = ['themeatandwineco.com', 'hunterandbarrel.com/au/']
    domain_list = ['ribsandburgers.com/au/', 'inghams.com.au', 'www.dfpartners.com.au', 'feelsbotanical.com.au']
    domain_list = ['dfpartners.com.au']
    domain_list = ['www.buenosystems.com.au', 'ami.org.au', 'speedcafe.com', 'winnings.com.au',
                   'www.appliancesonline.com.au', 'flintfox.com', 'www.marcels.co.nz', 'store.standards.org.au',
                   'perthzoo.wa.gov.au', 'www.roddandgunn.com/au', 'www.onehungamallclub.co.nz', 'www.flowpresso.co.nz',
                   'orionhealth.com/us/', 'www.goulburnrealestate.com.au', 'fabricofspringst.co.nz/', 'www.cos.net.au',
                   'heartbeatoffootball.com.au', 'www.sydneysymphony.com', 'www.attach2.com/au', 'www.vanessa-bell.com',
                   'www.spinalcure.org.au/']
    domain_list = ['www.mimeanalytics.com', 'independentdigitalaudit.com.au', 'www.onehungamallclub.co.nz',
                   'fabricofspringst.co.nz/']
    # domain_list = ['www.mimeanalytics.com']
    batch_size = 3
    batches = [domain_list[i:i + batch_size] for i in range(0, len(domain_list), batch_size)]

    for batch in batches:
        p = Process(target=run_spider_batch, args=(batch,))
        p.start()
        p.join()  # Wait for the process to finish


if __name__ == "__main__":
    run_spider()
