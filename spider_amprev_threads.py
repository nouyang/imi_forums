import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess

import numpy as np
import pandas as pd
# self.logger.info("Visited %s", response.url)

# for a given category 
# e.g. https://ampreviews.net/index.php?forums/discussion-pittsburgh.89/

# https://ampreviews.net/index.php?threads/lin-spa-brownsville-rd.133397/

class ThreadSpider(CrawlSpider):
    name = 'extract_threads'

    def start_requests(self):
        self.cities_crawled = set()
        self.base_url = 'https://ampreviews.net'
        data = pd.read_csv('_raw_forum.csv')

        # for category_url in data.link:
        category_url = 'https://ampreviews.net/index.php?forums/discussion-dallas.14/page-2' 
        self.logger.error(f'now working with url {category_url}')
        yield scrapy.Request(url=category_url, callback=self.parse_page)
        #self.logger.error('found link %s', category_link)

    def parse_page(self, response):
        category_text = response.css('.p-title-value::text').get() # e.g. Discussion-Dallas
        self.cities_crawled.add(category_text.split(' - ')[-1]) # e.g. Dallas 
        #self.state['cities_crawled'] = self.cities_crawled

        page_name = response.css('title::text').get() # e.g. Discussion-Dallas | Page 2 | AMPReviews
        page_url = response.url  

        for thread in response.css('div.structItem--thread'):
            title = thread.css('div.structItem-title a::text').get()
            link = thread.css('div.structItem-title a::attr(href)').get()
            num_replies, num_views = thread.css('dd::text').extract()

            author, latest_author = thread.css('a.username::text').extract()
            author_url, latest_author_url = thread.css('a.username::attr(href)').extract()

            posted_date_readable, latest_date_readable =  thread.css('time::attr(title)').extract()
            posted_date_data, latest_date_data =  thread.css('time::attr(data-time)').extract()

            # TODO: maybe refactor using first-child and second-child?
            # thread.css('dl:first-child dd').extract()

            scraped = {
                'title':title, 
                'num_replies': num_replies,
                'num_views': num_views, 
                'posted_date_readable': posted_date_readable, # Jan 23, 2003 at 6PM

                'author':author, 

                'latest_author':latest_author,
                'latest_date_readable': latest_date_readable , # e.g. 12345006

                'link':link,
                'author_url':author_url,
                'latest_author_url':latest_author_url ,
                'posted_date_data': posted_date_data,
                'latest_date_data': latest_date_data ,
                'comment': category_text,
            }

            yield scraped

        # dirty hack to insert "comment" into bottom of csv file
        # which contains the current page and url, just in case
        yield {
            'comment':page_name + ' ' +  page_url
        }

    # def followNext(self, response):
    #     next_page = response.css('a.pageNav-jump--next::attr(href)').get()
    #     if next_page is not None:
    #         next_page = response.urljoin(next_page)
    #         self.logger.error(f'going to next page: {next_page}')
    #         yield scrapy.Request(next_page, callback=self.parse)

c = CrawlerProcess(
    settings={
        "FEEDS":{
            "_tmp_threads.csv" : {"format" : "csv",
                                "overwrite":True,
                                "encoding": "utf8",
                            }},
        "DOWNLOAD_DELAY": 4,
        "DEPTH_LIMIT¶":2,
        #"JOBDIR":'crawls/amprev_threads'

    }
)
    #'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
    #'CLOSESPIDER_PAGECOUNT': 3,
c.crawl(ThreadSpider)
c.start()