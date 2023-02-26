# https://medium.com/hackernoon/how-to-scrape-websites-based-on-viewstates-using-scrapy-39feb9445755
# 25 Feb 2023
# Work to scrape govt data
# https://docs.scrapy.org/en/latest/faq.html#what-s-this-huge-cryptic-viewstate-parameter-used-in-some-forms

import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.crawler import CrawlerProcess

'''
<td>
<select name="ctl00$cphMainContent$ddlProfession" id="ctl00_cphMainContent_ddlProfession" tabindex="3" style="width:525px;">
    <option value="">All</option>
    <option value="146">Massage Therapist or Bodywork Therapist</option>
    <option value="46">Massage Therapist Or Bodyworker</option>
    <option value="47">Massage Therapist-No longer applicable-see #046 </option>
</select>
</td>
'''

class DecisionsSpider(scrapy.Spider):
    name = 'wi-decisions'
    start_urls = ['https://online.drl.wi.gov/orders/searchorders.aspx']

    def parse(self, response):
        print('\n!----')
	    # "ctl00$cphMainContent$ddlProfession": "146",
        profession_codes = [146, 46]
        # [a.attrib['href'] for a in response.css('a')]
        # text with the dollar signs
        profession_str = 'ctl00$cphMainContent$ddlProfession'
        print(response.css('body'))

        for option in response.css('select#ctl00_cphMainContent_ddlProfession > option'):
            profession_name = option.css("::text").extract_first()
            profession_value = option.css("::attr(value)").extract_first()

            if 'Massage' in profession_name:
                self.logger.error(f'{profession_name=}, {profession_value}')
                yield scrapy.FormRequest.from_response(
                    response, 
                    'https://online.drl.wi.gov/orders/searchorders.aspx',
                    formdata={
                        profession_str: profession_value,
                    },
                    callback=self.parse_results
            )
#'table#ctl_phMainContent_gvResults a ::attr(href)'

    def parse_results(self, response):
        for order in response.css('table#ctl_phMainContent_gvResults tr a ::attr(href)'):
            print(' \n ! ----')

            #yield {'name': profession_value}

'''
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
'''

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

c.crawl(DecisionsSpider)
c.start()