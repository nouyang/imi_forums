import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
import logging

logging.basicConfig(
    filename='log.txt',
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)


class QuotesSpider(CrawlSpider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com/tag/friendship/']
    #start_urls = ['https://quotes.toscrape.com/tag/friendship/']

    def start_requests(self):
        urls = ['https://quotes.toscrape.com/tag/friendship/']
        for url in urls:
            self.logger.info('Parse function called on %s', url)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response): # scrapy's default callback method
        for quote in response.css('div.quote'):
            text = quote.css('span.text::text').get()
            self.log(f'Found text {text}')
            yield {
                'text': text 
                }

        next_page = response.css('li.next a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

c = CrawlerProcess(
    settings={
        "FEEDS":{
            "friendship.csv" : {"format" : "csv",
                                "overwrite":True}},
        "DOWNLOAD_DELAY": 10,
    }
)
    #'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
    #'CLOSESPIDER_PAGECOUNT': 3,
c.crawl(QuotesSpider)
c.start()