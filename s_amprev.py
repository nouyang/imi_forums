import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
# self.logger.info("Visited %s", response.url)

# for all links on page
    # in link contains reviews or disucssions 
        # get the # threads or # messages
        # yield (stop following)
    # else if the link ctonaines rcategories
    # follow the link and parse again 
#class CategoryItem(scrapy.Item):
    #title = scrapy.Field() 
    #link = scrapy.Field()
    #num_threads =  scrapy.Field()
    #num_messages = scrapy.Field()


# TODO 2/1/2023: Don't duplicate cities
class AmpRevSpider(CrawlSpider):
    name = 'extract_cities'
    start_urls = ['https://ampreviews.net/index.php']
    #allowed_domains = 'https://ampreviews.net/index.php'

    def start_requests(self):
        self.cities = set()
        self.base_url = 'https://ampreviews.net'

        url = 'https://ampreviews.net/index.php'
        self.logger.error(f'starting with url {url}')
        yield scrapy.Request(url=url, callback=self.parse_item)

            #self.logger.error('found link %s', category_link)
    def parse_item(self, response):
        for category in response.css("div.node-main"):
            category_link = category.css("a::attr(href)").extract_first() 

            if 'reviews-' in category_link or 'discussion-' in category_link:
                num_threads, num_msgs = category.css("dd::text").extract()
                title = category.css("a::text").get()
                city = title.split(' - ')[-1]

                self.logger.info(f'Got city: {city}, from link: {category_link}')
                self.cities.add(city)

                yield{
                    #'cities': self.cities,
                    'city': city,
                    'title': title,
                    'link': category_link,
                    'num_threads':   num_threads,
                    'num_messages': num_msgs
                }
                self.logger.debug(f'List of cities so far: {self.cities}')

            elif 'categories' in category_link:
                constructed_url = self.base_url + category_link
                self.logger.info(f'!-- Recursing down to {constructed_url}')
                yield scrapy.Request(url=constructed_url, callback=self.parse_item)
            
    #custom_settings = {'FEED_URI': '/Desktop/bbdata.csv','ITEM_PIPELINES':{'bb.pipelines.BBPipeline':300},'FEED_FORMAT':'csv'}
#
c = CrawlerProcess(
    settings={
        "FEEDS":{
            "_raw_forum.csv" : {"format" : "csv",
                                "overwrite":True,
                                "encoding": "utf8",
                            }},
        "DOWNLOAD_DELAY": 4,
    }
)
    #'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36',
    #'CLOSESPIDER_PAGECOUNT': 3,
c.crawl(AmpRevSpider)
c.start()