import json
import re
import scrapy
from scrapy.crawler import CrawlerProcess
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

class EmailSpider(scrapy.Spider):
    name = 'email'
    start_urls = ['https://www.advokomfbih.ba/spisak-advokata-regionalnih-komora-u-federaciji-bosne-i-hercegovine/']
    def parse(self,response):
        items = response.xpath('//*[@id="tablepress-1"][./tbody]//tr')
        data = {}
        data['emails'] = []
        for item in items:
            email = item.css("td:nth-child(3)::text").get()
            if email is not None:
                splited = email.split()
                for s in splited:
                    is_valid = check(s)
                    
                    if is_valid:
                        data['emails'].append({
                            'email': s,
                            'sent': False
                        })
        with open('emails.json', 'w') as o:
            json.dump(data, o)
 
def check(email):
    
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False   
    
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(EmailSpider)
    process.start()