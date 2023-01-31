import scrapy
from scrapy.linkextractors import LinkExtractor
# self.logger.info("Visited %s", response.url)

# for all links on page
    # in link contains reviews or disucssions 
        # get the # threads or # messages
        # yield (stop following)
    # else if the link ctonaines rcategories
    # follow the link and parse again 

class AmpRevSpider(CrawlSpider):
    name = 'extractlinks'
    #allowed_domains = ['https://ampreviews.net/index.php?']
    start_urls = ['https://ampreviews.net/index.php?']
    base_url = 'https://ampreviews.net'
    #rules = #[Rule(LinkExtractor(), callback='parse_item', follow=True)]
    #rules = [Rule(LinkExtractor(allow='categories'),

    def __init__(self):
        self.links = []

    def parse_item(self, response):
        for category in response.css("div.node-main"):

            category_link = category.css("a::attr(href)") 

            if 'reviews-' in category_link or 'discussion-' in category_link:
                num_threads, num_msgs = category.css("dd::text").extract()
                yield{
                    'Title': category.css("a::text").extract_first(),
                    'Link': category_link, 
                    'No. Threads':  num_threads, 
                    'No. Messages': num_msgs
                }
            else:
                yield response.follow(url=(base_url + category_link), callback=self.parse_item)
            
