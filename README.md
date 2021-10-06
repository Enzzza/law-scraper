

<img src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/IEEE.jpg" data-canonical-src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/IEEE.jpg" width="600"/>


<br>
<br>


# This code is made for purpose of program IEEE Innovation Nation

## 1. Finding some basic demographics

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

<p>After execution of this script we will get <strong><em>names.json</em></strong> file with names and genders.</p>

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
<img src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/graph.png" data-canonical-src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/IEEE.jpg" width="400"/>

<br>
<br>
<br>

## 2. Scraping names, emails of lawyers for survey purpose

<p>For our survey, we needed to get emails and names so that we can personalize our emails.</p>

Code for this is shown bellow.

email_and_name_scraper.py

```python
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

```

<p>After execution of this script we will get <strong><em>lawyers.json</em></strong> file with names and emails.</p>


<br>
<br>
<br>

## 3. Sending personalized emails to our target group

### Generating sqlite database

<p>For easier tracking which lawyer is contacted we will make sqlite database from our <strong><em>lawyers.json</strong></em> file </p>
<p>Generating <strong>lawyers.db</strong> file</p>

```python
import sqlite3
import json
import uuid



def connect_to_db(dbName):
    global conn
    global c
    conn = sqlite3.connect(f"{dbName}.db")
    c = conn.cursor()

def create_table():
    c.execute("""CREATE TABLE lawyers (
            id text UNIQUE,
            name text,
            email text,
            sent integer
            )""")

def insert_lawyer(name, email):
    id = str(uuid.uuid4())
    with conn:
        c.execute("INSERT INTO lawyers VALUES (:id, :name, :email, :sent)", {'id':id, 'name': name, 'email': email, 'sent': False})

def insert_from_json():
    with open('lawyers.json') as json_file:
        data = json.load(json_file)
        for l in data['lawyers']:
            insert_lawyer(l["name"],l["email"])

def print_database():
    c.execute("SELECT * FROM lawyers")
    print(c.fetchall())


def main():
    connect_to_db("lawyers")
    create_table()
    insert_from_json()
    print_database()
    

if __name__ == "__main__":
    main()    
```

### Creating template for our email

