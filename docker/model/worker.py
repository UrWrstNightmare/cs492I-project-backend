from transformers import pipeline
import torch
import pika
from pymongo import MongoClient

from PIL import Image
import requests
from io import BytesIO

# Mongo Conenction
client = MongoClient('cs492_mongodb', 27017)

db = client["cs492"]
job_collection = db["job-collection"]


def url2img(url):
  img_content = requests.get(url).content
  img = Image.open(BytesIO(img_content))
  if img.mode != "RGB":
    img = img.convert(mode="RGB")
  return img


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')) # Connect this part to swarm network (and point to RabbitMQ)
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())

    _body = body.decode()

    job_collection.update_one({ "id": _body.id }, { "status": "working" })
    
    # TODO: Add Model Integration Here
    res = ""

    job_collection.update_one({ "id": _body.id }, { "status": "complete", "alt": res })

    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

channel.start_consuming()