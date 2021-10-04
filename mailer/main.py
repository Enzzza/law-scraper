from datetime import timedelta
from email_sender import email_task
from redis import Redis
from rq import Queue, queue


q = Queue(connection=Redis(host='redis',port=6379))

job = q.enqueue_in(timedelta(seconds=60),email_task)