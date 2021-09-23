import json
import scrapy
from scrapy.crawler import CrawlerProcess
import gender_guesser.detector as gender

class LawyerSpider(scrapy.Spider):
    name = 'lawyer'
    start_urls = ['https://www.advokomfbih.ba/spisak-advokata-regionalnih-komora-u-federaciji-bosne-i-hercegovine/']
    def parse(self,response):
        items = response.xpath('//*[@id="tablepress-1"][./tbody]//tr[./td]')
        d = gender.Detector()
        data = {}
        data['names'] = []
        for item in items:
            td_first = item.xpath(".//td/text()").get()
            if td_first is not None:
                splited = td_first.split()
                for s in splited:
                    guessed = d.get_gender(s)
                    
                    if guessed != "unknown":
                        data['names'].append({
                            'name': s,
                            'gender': guessed,
                        })
        with open('names.json', 'w') as o:
            json.dump(data, o)
 
    
    
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(LawyerSpider)
    process.start()