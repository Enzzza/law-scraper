

<img src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/IEEE.jpg" data-canonical-src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/IEEE.jpg" width="600"/>


<br>
<br>


# This code is made for purpose of program IEEE Innovation Nation

## Finding some basic demographics

<p>Our task was to research our target market. And that market consists of lawyers.</p> <p>
As there were no public demographics statistics available for this particular group of people, we wanted to find some basic information.
To find some demographics information we scraped data from a public site that has a database of all active lawyers in FBiH.
Our goal was to extract names so we can guess by the name if it's male or female and in this way, we would get a percentage of males and females in the lawyers' fields of work. </p> Table that we scraped didn't have harmonized data set. For example, some data were in this format:

- lastname husband-lastname name
- name lastname
- degree name lastname
- ...

<p>Code for this job:</p>

lawyers_scraper.py

```python
import json
import scrapy
from scrapy.crawler import CrawlerProcess
import gender_guesser.detector as gender

class LawyerSpider(scrapy.Spider):
    name = 'lawyer'
    start_urls = ['https://www.advokomfbih.ba/spisak-advokata-regionalnih-komora-u-federaciji-bosne-i-hercegovine/']
    def parse(self,response):
        items = response.xpath('//*[@id="tablepress-1"][./tbody]//tr')
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

```

<p>After execution of this script we will get *json* file with names and genders.</p>

### Creating basic graph

<p>With this data we can generate basic graph.</p>
generate_graph.py

```python
import json
import matplotlib.pyplot as plt


def counter():
    m = 0
    f = 0
    
    with open('names.json') as json_file:
        data = json.load(json_file)
        for n in data['names']:
            if n['gender'] == 'male':
                m += 1
            else:
                f += 1
    return m, f

if __name__ == "__main__":
    m, f = counter()
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = 'Male', 'Female'
    sizes = [(m*100/(m+f)),(f*100/(m+f))]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    #plt.show()
    plt.savefig('graph.png')

```

