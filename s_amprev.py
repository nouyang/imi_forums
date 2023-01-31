import scrapy
import logging

class AmpRevSpider(scrapy.spider):
    name = 'categories'
    allowed_domains = ['https://ampreviews.net/index.php?']
    start_urls = ['https://ampreviews.net/index.php?']

    def parse(self, response):
        # mix of city and state names on homepage 
        homepage_categories = response.css("h2.block-header").css("a")
        for categ in homepage_categories:
            name = response.css("h2.block-header").css("a::attr(href)").extract()
            link = response.css("h2.block-header").css("a::text").extract()

        yield response.follow(url=link, callback = self.parse_homepage, meta=['homepg_categ_name':name]
    
    def parse_country(self, response):
        name =  'test'



from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

# https://medium.com/quick-code/python-scrapy-tutorial-for-beginners-04-crawler-rules-and-linkextractor-7a79aeb8d72

class AmpRevSpider(CrawlSpider):
    name = 'amp_reviews_spider'
    allowed_domains = ['https://ampreviews.net/index.php?']
    start_urls = ['https://ampreviews.net/index.php?']
    base_url = 'https://ampreviews.net/index.php?'


    "h2.block-header > a::text"
    "h2.block-header > a::attr(href)"
    "h3.block-header > a::attr(href)"
    # actually... ultimately we don't care about preserving what's the state or city... just review / discusison... and the thread name is right there...


    # https://ampreviews.net/index.php?forums/reviews-allentown.78/
    # https://ampreviews.net/index.php?forums/discussion-allentown.79/

    rules = (
        #Rule(LinkExtractor(restrict_css=".nav-list > li > ul > li > a"), follow=True),
        #Rule(LinkExtractor(restrict_css=".product_pod > h3 > a"), callback="parse_book")
    )

    def parse_categs(self, response):
        if 'reviews-' not in categ_url or 'discussion-' not in categ_url:
            next_pg_url = response.css("h2.block-header > a::attr(href)").extract_first()
            yield scrapy.Request(next_pg_url, callback = self.parse_categs)
        else:
            city_name = 
            link = categ_url
            num_threads = 

            yield{
                'City Name': title, 
                'Link': link,  
                'Number of Threads':  num_threads,
                'Number of Messages' num_msgs
            }

        # self.logger.info("Visited %s", response.url)

# Pseud code
# for all links on page
    # in link contains reviews or disucssions 
        # get the # threads or # messages
        # yield (stop following)
    # else if the link ctonaines rcategories
    # follow the link and parse again 



    #for link in self.link_extractor.extract_links(response):
        #yield Request(link.url, callback=self.parse)

    #<h2 class="block-header">
				#<a href="/index.php?categories/chicago.9/">Chicago</a>
			#</h2>
    # <h3 class="node-title">
    #   <a href="/index.php?forums/reviews-chicago.10/"
    #   data-xf-init="element-tooltip" data-shortcut="node-description">Reviews #   - Chicago</a> 
    # </h3>

    #rules = [Rule(LinkExtractor(allow='categories'),
                    #callback='parse_filter_book', follow=True)]

    #def 

   yield {
    'Thread':

   } 

    # Parse for homepage categ links 
    yield {
        'Level': 0 #1, 2, 3 levels deep
        'Parent': None # Name of direct parent 
        'Title': None # Title of itself
        'Link': # link to itself
        'No. Threads':  
        'No. Messages'
   }

# home page has list of cities (or locations)
# each city has either discussion or reviews
# each discussion page has a list of threads (paginated)
# each thead can have multiple pages

class AmpRevSpider(CrawlSpider):
    name = 'extractlinks'
    #allowed_domains = ['https://ampreviews.net/index.php?']
    start_urls = ['https://ampreviews.net/index.php?']
    #base_url = 'https://ampreviews.net/index.php?'
    #rules = #[Rule(LinkExtractor(), callback='parse_item', follow=True)]
    #rules = [Rule(LinkExtractor(allow='categories'),

    def __init__(self):
        self.links = []

    def parse_item(self, response):
        for category in reponse.css("div.node-main"):
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
                yield scrapy.Request(category_link, callback=self.parse_item)
            
