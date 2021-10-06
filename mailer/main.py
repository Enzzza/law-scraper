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