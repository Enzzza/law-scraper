

<img src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/IEEE.jpg" data-canonical-src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/IEEE.jpg" width="600"/>


<br>
<br>


# This code is made for purpose of program IEEE Innovation Nation

## **1. Finding some basic demographics**

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

## **2. Scraping names, emails of lawyers for survey purpose**

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

## **3. Sending personalized emails to our target group**
<br>

### **Generating sqlite database**
<br>
<p>For easier tracking which lawyer is contacted we will make sqlite database from our <strong><em>lawyers.json</strong></em> file </p>
<p>Generating <strong>lawyers.db</strong> file</p>

populate_sqlite.py
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
<br>

### **Creating template for our email**

<br>

>Look of our template

<br>

<img src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/email_template.PNG" data-canonical-src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/email_template.PNG" width="400"/>

### **Sending emails to lawyers**

<p>To send email we will use built in python library </p>

email_sender.py
```python
import os
import sqlite3
import smtplib
import codecs
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()
 
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_ADDRESS_FINAL = os.environ.get("EMAIL_ADDRESS_FINAL")
 
def connect_to_db(dbName):
    global conn
    global c
    conn = sqlite3.connect(f"{dbName}.db")
    c = conn.cursor()
 
def send_mail(subject, to_address, txt_content, html_content=None):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_address
 
 
    msg.set_content(txt_content)
    if html_content is not None:
        msg.add_alternative(html_content, subtype='html')
 
 
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
 
def get_content(name):
 
    if name is None:
        name = "there"
        footer_msg = "Thank you very much."
    else:
        footer_msg = f"Thank you, {name}."
 
    html_file = codecs.open("html_content.html", "r", "utf-8")
    html_content = html_file.read()
    html_content = html_content.replace("[name]", name)
    html_content = html_content.replace("[footer_msg]", footer_msg)
 
    with open('txt_content.txt') as f:
        txt_content = f.read()
 
    txt_content = txt_content.replace("[name]", name)
 
    return txt_content, html_content
 
def get_username():
    c.execute("SELECT * FROM lawyers WHERE sent=0")
    values = c.fetchone()
    if values is not None:
        return values
 
    return None
 
def update_sent_status(id):
    with conn:
        c.execute("""UPDATE lawyers SET sent = 1
                    WHERE id = :id""",
                  {'id': id })
 
def email_task(num_of_mails, i):
    connect_to_db("lawyers")
    values = get_username()
    if values is not None:
        (id, name, email, _) = values
        txt_content, html_content = get_content(name)
        try:
            send_mail('Want to see the future of the legal profession in BiH?', email, txt_content, html_content)
            print(f"Sending email to {email} [{i+1}/{num_of_mails}]")
        except:
            print("Something went wrong")
        else:
            update_sent_status(id)
    else:
        send_mail('[INFO] AI Lawyer mailer',EMAIL_ADDRESS_FINAL, f"All of {num_of_mails} mails sent!")
        print(f"All of {num_of_mails} mails sent!")
```

<p>But to be able to send all emails we need to use queue solution. </p>

 This solution can be found in [rq python](https://python-rq.org/) library

main.py
 ```python 
 import redis
from rq import Queue
import sqlite3
import humanize
import datetime as dt
import math
from email_sender import email_task
 
def connect_to_db(dbName):
    global conn
    global c
    conn = sqlite3.connect(f"{dbName}.db")
    c = conn.cursor()
 
def main():
    connect_to_db("lawyers")
    c.execute("SELECT * FROM lawyers WHERE sent=0")
    num_of_mails = len(c.fetchall())
    g_mail_limit = 500
    duration_between = math.floor(24 * 60 * 60 / g_mail_limit)
 
    print(f"TO send this mails it will take {humanize.naturaldelta(dt.timedelta(seconds=num_of_mails*duration_between))}")
    r = redis.Redis()
    q = Queue(connection=r)
 
    if num_of_mails != 0:
        for m in range(num_of_mails):
            job = q.enqueue_in(dt.timedelta(seconds=duration_between*m), email_task, num_of_mails, m)
            print(job)
 
    else:
        job = q.enqueue_in(dt.timedelta(seconds=duration_between), email_task, num_of_mails, 0)


if __name__ == "__main__":
    main()
```

<p>To start sending this emails we need to activate rq worker</p>

```bash 
rq worker -s
```
<img src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/rq_worker.PNG" data-canonical-src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/rq_worker.PNG" width="600"/>
<br>
<br>

><p>In our case we are running the script on a digitalocean droplet we need to ensure that script will run after we close ssh connection to our droplet instance and that is possible with the use of command nohup</p>
<br>

```bash
nohup rq worker -s

# and if we want to see content of stdout 

tail -f nohup.out
```



<p>Than run <strong>main.py</strong> script</p>

```bash 
python main.py
```

<img src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/main_py.PNG" data-canonical-src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/main_py.PNG" width="600"/>

<br>
<br>

<p>We are using a queue to enqueue tasks in Redis database.</p> 
<p>This script will send an email every 170 seconds.</p>

<br>

> *example of received email.*
<img src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/email_recived.PNG" data-canonical-src="https://raw.githubusercontent.com/Enzzza/law-scraper/master/media/email_recived.PNG" width="800"/>

