# https://medium.com/hackernoon/how-to-scrape-websites-based-on-viewstates-using-scrapy-39feb9445755
# 25 Feb 2023
# Work to scrape govt data
# https://docs.scrapy.org/en/latest/faq.html#what-s-this-huge-cryptic-viewstate-parameter-used-in-some-forms

import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerProcess


class SpidyQuotesViewStateSpider(scrapy.Spider):
    name = 'spidyquotes-viewstate'
    start_urls = ['http://quotes.toscrape.com/search.aspx']
    download_delay = 1.5    

    def parse(self, response):
        for author in response.css('select#author > option ::attr(value)').extract():
            yield scrapy.FormRequest(
                'http://quotes.toscrape.com/filter.aspx',
                formdata={
                    'author': author,
                    '__VIEWSTATE': response.css('input#__VIEWSTATE::attr(value)').extract_first()
                },
                callback=self.parse_tags
            )    

    def parse_tags(self, response):
        for tag in response.css('select#tag > option ::attr(value)').extract():
            yield scrapy.FormRequest.from_response(
                response,
                formdata={'tag': tag},
                callback=self.parse_results,
            )

    def parse_results(self, response):
        for quote in response.css("div.quote"):
            #self.logger.info(f'Quote: {response.css("span.content ::text").extract_first()}')
            yield {
                'quote': response.css('span.content ::text').extract_first(),
                'author': response.css('span.author ::text').extract_first(),
                'tag': response.css('span.tag ::text').extract_first(),
            }

c = CrawlerProcess(
    settings={
        "FEEDS":{
            "_tmp_posts.csv" : {"format" : "csv",
                                "overwrite":True,
                            }},
        "CONCURRENT_REQUESTS":1, # default 16
        "DOWNLOAD_DELAY": 0.2, # default 0
    }
)

c.crawl(SpidyQuotesViewStateSpider)
c.start()