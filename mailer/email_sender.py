import os
import sqlite3
import smtplib
import codecs
import json
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

def email_task():
    connect_to_db("test_lawyers")
    values = get_username()
    if values is not None:
        (id, name, email, _) = values
        txt_content, html_content = get_content(name)
        try:
            send_mail('Be part of future, AI Lawyer needs you!', email, txt_content, html_content)
        except:
            print("Something went wrong")
        else:
            update_sent_status(id)
    else:
        send_mail('[INFO] AI Lawyer mailer',EMAIL_ADDRESS_FINAL, "All mails sent!")
        
