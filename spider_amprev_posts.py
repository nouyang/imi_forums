import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerProcess
import logging
from scrapy.utils.log import configure_logging 

import numpy as np
import pandas as pd
# self.logger.info("Visited %s", response.url)

# for a given category 
# e.g. https://ampreviews.net/index.php?forums/discussion-pittsburgh.89/

# https://ampreviews.net/index.php?threads/lin-spa-brownsville-rd.133397/

class PostSpider(CrawlSpider):
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%d/%b/%Y %H:%M:%S',
        level=logging.info
    )
    name = 'extract_posts'

    def start_requests(self):
        self.cities_crawled = set()
        self.base_url = 'https://ampreviews.net'

        post_url = '/index.php?threads/building-a-list-of-he-only-spots-in-manhattan.129971/' 
        url = self.base_url + post_url 
        self.logger.error(f'now working with url {url}')
        yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        max_pages = response.css('li.pageNav-page:last-child a::text').get()

        category_text = response.css('.p-title-value::text').get() # e.g. Discussion-Dallas
        self.cities_crawled.add(category_text.split(' - ')[-1]) # e.g. Dallas 
        self.state['cities_crawled'] = self.cities_crawled

        page_name_and_pagination = response.css('title::text').get() # e.g. Discussion-Dallas | Page 2 | AMPReviews
        page_url = response.url  

        posts = response.css('article.message--post').get()

        for post in posts: 
            #for post in response.css('div.bbWrapper'):

            # - get post metadata
            post_link = post.css 
            post_id = post.css('::attr(data-content').get()
            # example link: "/index.php?threads/building-a-list-of-he-only-spots-in-manhattan.129971/post-954437" 
            
            posted_date_readable = post.css('div.message-date time::attr(title)').get()
            posted_date_data = post.css('div.message-date time::attr(title)').get()
            post_num = post.css('.message-attribution-opposite a::text').get().strip().split()[-1]

            post_text = post.css('div.bbWrapper::text').getall()

            quotes = post.css('div.bbCodeBlock--quote').get()
            # WHAT IF THERE'S TWO QUOTES 0:

            if quotes: 
                num_quotes = 0
                quoted_post_ids = []
                quoted_authors = []
                quoted_content = []
                for quote in quotes:
                    num_quotes += 1
                    quoted_post_id = quote.css('.bbCodeBlock-sourceJump::attr(data-content-selector)').extract()
                    quoted_post_ids.append(quoted_post_id)

                    quoted_author = quote.css('a::text').get().split()[0]
                    quoted_authors.append(quoted_author)
                    quoted_post_content = quote.css(
                        '.bbCodeBlock-expandContent::text').get()   
                    quoted_content.append(quoted_post_content)
                ' ~~ '.join(quoted_ids) 
                ' ~~ '.join(quoted_authors) 
                ' ~~ '.join(quoted_content) 
            likers = nopost.css('div.likesBar a * ::text').getall()
            likers = ' - '.join(likers)
            # If want ot parse newlines in html, and ignore other text: In [72]: ' '.join(quote.xpath('//div[@class="bbCodeBlock-expandContent"]//text()').getall())

            # - Author stats 
            author = post.css('::attr(data-author').get()
            author_url = post.css('div.message-userDetails a.username::attr(href)').get()
            author_title, author_num_posts, author_num_reviews = post.css('h5.message-userTitle ::text').getall()[:3]
            # Example output: ['Review Contributor', 'Messages: 46', 'Reviews: 13', 'Joined ', 'Oct 2, 2019']
            join_date_readable = post.css('.userTitle time::attr(title)').get()
            join_date_data  = post.css('div.message-userDetails .userTitle time::attr(data-time)').get()



            self.logger.info(f'Now scraping: {page_name_and_pagination} -- {page_url} -- TotalPages {max_pages}')

            scraped = {
                'title':title, 
        
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
        "DOWNLOAD_DELAY": 10, # default 0
        "DEPTH_LIMIT":1,
        "JOBDIR":'crawls/amprev_threads',
        "DUPEFILTER_DEBUG":True,
    }
)

    #'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
    #'CLOSESPIDER_PAGECOUNT': 3,
c.crawl(PostSpider)
c.start()