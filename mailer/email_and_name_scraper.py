import json
import re
import scrapy
from scrapy.crawler import CrawlerProcess
import gender_guesser.detector as gender
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

class LawyersSpider(scrapy.Spider):
    name = 'lawyers'
    start_urls = ['https://www.advokomfbih.ba/spisak-advokata-regionalnih-komora-u-federaciji-bosne-i-hercegovine/']
    def parse(self,response):
        infos = response.xpath('//*[@id="tablepress-1"][./tbody]//tr')
        d = gender.Detector()
        data = {}
        data['lawyers'] = []
        for info in infos:
            email = info.css("td:nth-child(3)::text").get()
            name = info.xpath(".//td/text()").get()
            valid_name = None
            valid_email = None
            valid_gender = None
            
            if email is not None:
                splited = email.split()
                for s in splited:
                    is_valid = check(s)
                    
                    if is_valid:
                        valid_email = s
            
            if name is not None:
                splited = name.split()
                for s in splited:
                    guessed = d.get_gender(s)
                    
                    if guessed != "unknown":
                        valid_name = s
                        valid_gender = guessed
            
            if valid_email is not None:
                data["lawyers"].append({
                    'name': valid_name,
                    'email': valid_email,
                    'gender': valid_gender,
                    'sent': False
                })
            
        with open('lawyers.json', 'w') as o:
            json.dump(data, o)
        
 
def check(email):
    
    if(re.fullmatch(regex, email)):
        return True
    else:
        return False   
    
if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(LawyersSpider)
    process.start()