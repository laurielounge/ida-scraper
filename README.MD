# Scrapy Service #
This is IDA's scraping service. It's a Scrapy project that scrapes websites for data.
It uses selenium to break scrape busters and render javascript.
## Background ##
scrapy looks like this. It needs four files really to run, in scraper_details:
middlewares
pipelines
settings
and spiders/ida_audit.py
It caches the sites in .scrapy/httpcache. The cache files have a lifespan controlled in settings.py.
If you break an audit and rerun, it will use the files that are cached. selenium will NOT re-render them. It doesn't need to.

## Running ##

You're here because audit x hasn't run.

Go to run_scrap.py and stick the audit_id in there.

Actually, don't do that. Problems with the background processing debugging. You can't see it.

Instead, scraper_details/settings.py change logging level to DEBUG.
Then load the venv (use "uv") and then:

```bash
scrapy crawl ida_audit -a audit_id=89 -a api_identifier="http://www.blum.com/au/en/"
````

or

```bash
scrapy crawl ida_audit -a api_identifier="https://au.au.vushstimulation.com" -a audit_id=100 -s LOG_LEVEL=INFO
nohup scrapy crawl ida_audit -a api_identifier="https://au.vushstimulation.com/" -a audit_id=100 -s LOG_LEVEL=INFO > spider_output.log 2>&1 &
scrapy crawl ida_audit -a api_identifier=www.mimeanalytics.com -a audit_id=38 -s LOG_LEVEL=INFO
scrapy crawl ida_audit -a api_identifier=ozdesignfurniture.com.au/ -a audit_id=94 -s LOG_LEVEL=INFO
````

OR

```bash
curl -X GET "http://scraper:8000/api/scrape/100" -H "User-Agent: python-requests/2.31.0" -H "Accept-Encoding: gzip, deflate" -H "Accept: */*" -H "Connection: keep-alive" -H "x-api-key: 9qQQdRdmvLKZxxuP7tj6DYFMpmeLcdXk"
```

or more politely

```bash
curl -X GET "http://scraper:8000/api/scrape/96" \
-H "User-Agent: python-requests/2.31.0" \
-H "Accept-Encoding: gzip, deflate" \
-H "Accept: */*" \
-H "Connection: keep-alive" \
-H "x-api-key: 9qQQdRdmvLKZxxuP7tj6DYFMpmeLcdXk"
```
