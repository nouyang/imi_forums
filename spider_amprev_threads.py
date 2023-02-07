import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerProcess
import logging
from scrapy.utils.log import configure_logging 

import numpy as np
import pandas as pd
# NOTE: if running into struct error needs unpack 4 bytes,
# remove the job dir (cralws/amprev); make sure to stop scrapy with a
# single ctrl-c, which will take 'download-delay' seconds to take effect

# self.logger.info("Visited %s", response.url)

# for a given category 
# e.g. https://ampreviews.net/index.php?forums/discussion-pittsburgh.89/

# https://ampreviews.net/index.php?threads/lin-spa-brownsville-rd.133397/

class ThreadSpider(CrawlSpider):
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%d/%b/%Y %H:%M:%S',
        level=logging.INFO
    )
    name = 'extract_posts'

    def __init__(self):
        self.cities_crawled = set()

        configure_logging(install_root_handler=False)
        logging.basicConfig(
            filename='log.txt',
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%d/%b/%Y %H:%M:%S',
            #level=logging.INFO # TODO:debug, has no effect 
        )

    def start_requests(self):
        self.base_url = 'https://ampreviews.net'
        forum_data = pd.read_csv('_raw_forum.csv')
        #forum_data = pd.read_csv('_tmp_forum.csv')

        #category_url = 'ampreviews.net/index.php?forums/discussion-dallas.14/page-2' 
        for category_url in forum_data.link:
            url = self.base_url + category_url
            self.logger.error(f'now working with url {url}')
            yield scrapy.Request(url=url, callback=self.parse_page)
        #self.logger.error('found link %s', category_link)

    def parse_page(self, response):
        max_pages = response.css('li.pageNav-page:last-child a::text').get()

        category_text = response.css('.p-title-value::text').get() # e.g. Discussion-Dallas
        self.cities_crawled.add(category_text.split(' - ')[-1]) # e.g. Dallas 
        self.state['cities_crawled'] = self.cities_crawled

        page_name_and_pagination = response.css('title::text').get() # e.g. Discussion-Dallas | Page 2 | AMPReviews
        page_url = response.url  

        for thread in response.css('div.structItem--thread'):
            title = thread.css('div.structItem-title a::text').get()
            link = thread.css('div.structItem-title a::attr(href)').get()
            num_replies, num_views = thread.css('dd::text').extract()
            #self.logger.debug(f'now parsing: {title}')

            author = thread.css('a.username:first-child::text').get()
            latest_author = thread.css('a.username:last-child::text').get()
            #self.logger.debug(f'now parsing usernames: {author}, {latest_author}')

            author_url, latest_author_url = thread.css('a.username::attr(href)').extract()

            posted_date_readable, latest_date_readable =  thread.css('time::attr(title)').extract()
            posted_date_data, latest_date_data =  thread.css('time::attr(data-time)').extract()

            self.logger.info(f'Now scraping: {page_name_and_pagination} -- {page_url} -- TotalPages {max_pages}')

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
            'comment': f'{page_name_and_pagination} -- {page_url} -- TotalPages {max_pages}'
        }

        next_page = response.css('a.pageNav-jump--next::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            self.logger.info(f'going to next page: {next_page}')
            yield scrapy.Request(next_page, callback=self.parse_page)

c = CrawlerProcess(
    settings={
        "FEEDS":{
            "_tmp_threads.csv" : {"format" : "csv",
                                "overwrite":True,
                                "encoding": "utf8",
                            }},
        "CONCURRENT_REQUESTS":1, # default 16
        "CONCURRENT_REQUESTS_PER_DOMAIN":1, # default 8 
        "CONCURRENT_ITEMS":1, # DEFAULT 100
        "DOWNLOAD_DELAY": 15, # default 0
        #"DEPTH_LIMIT":1,
        "JOBDIR":'crawls/amprev_threads',
        "DUPEFILTER_DEBUG":True,
    }
)
    #'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
    #'CLOSESPIDER_PAGECOUNT': 3,
c.crawl(ThreadSpider)
c.start()
