from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import HttpUrl, BaseModel, Field

from fastapi.logger import logger

from transformers import pipeline
from pymongo import MongoClient
import torch

from PIL import Image
import requests
from io import BytesIO

import pika
import uuid
import json

app = FastAPI()

# RabbitMQ Connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host='cs492_rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

# MongoDB Connection
client = MongoClient('cs492_mongodb', 27017)
db = client["cs492"]

job_collection = db["job-collection"]
data_log = db["data-log"]


# Routes Definition
@app.get("/")
async def root():
    return {"message": "Hello World"}


def url2img(url):
  img_content = requests.get(url).content
  img = Image.open(BytesIO(img_content))
  if img.mode != "RGB":
    img = img.convert(mode="RGB")
  return img

class PredictionInput(BaseModel):
    url: str

class PredictionInputV2(BaseModel):
    url: str
    context: str

class CheckStatusV2(BaseModel):
    uuid: str

class UserSelectV2(BaseModel):
    url: str
    context: str
    selected_text: str

class UserALTV2(BaseModel):
    url: str
    context: str
    user_alt: str

@app.post("/api/v1/predict")
async def predict(body: PredictionInput):
    logger.info(f"[API][PREDICT] V1 PREDICT API Called")
    logger.info(f"[API][PREDICT] Input URL: { body }")

    # model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    # feature_extractor = ViTFeatureExtractor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    # tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # model.to(device)

    logger.info(f"[API][PREDICT] Model Loaded!")

    image_to_text = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")
    prediction_str = image_to_text(body.url)
    
    logger.info(f"[API][PREDICT] results: { prediction_str }")

    return {
        "alt": prediction_str[0]["generated_text"]
    }

    # image = url2img(body.url)
    
    # pixel_values = feature_extractor(images=[image], return_tensors="pt").pixel_values
    # pixel_values = pixel_values.to(device)

    # max_length = 16
    # num_beams = 4
    # gen_kwargs = {"max_length": max_length, "num_beams": num_beams}
    # output_ids = model.generate(pixel_values, **gen_kwargs)


@app.post("/api/v2/predict")
async def predictv2(body: PredictionInputV2):
    logger.info(f"[API][PREDICT] V2 PREDICT API Called")
    logger.info(f"[API][PREDICT] Input URL: { body }")

    job_uuid = uuid.uuid4()
    message = json.dumps({
        "id": job_uuid,
        "url": body.url,
        "context": body.context
    })

    job_entry = {
        "id": job_uuid,
        "status": "pending"
    }

    channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
    ))

    job_collection.insert_one(job_entry)

    logger.info(f"[API][PREDICT] Dispatch to worker complete")
    
    return {
        "status": "OK",
        "job_uuid": job_uuid
    }

@app.post("/api/v2/check_status")
async def check_status(body: CheckStatusV2):
    logger.info(f"[API][PREDICT] V2 CHECK STATUS API Called")
    logger.info(f"[API][PREDICT] Input URL: { body }")

    res = job_collection.find_one({ "id": body.uuid })

    return {
        "status": "OK",
        "payload": json.dumps(res)
    }


@app.post("/api/v2/user_select")
async def user_select(body: UserSelectV2):
    payload = {
        "type": "SELECTED",
        "url": body.url,
        "context": body.context,
        "alt": body.selected_text
    }

    data_log.insert_one(payload)

    return {
        "status": "OK"
    }

@app.post("/api/v2/user_alt")
async def user_alt(body: UserALTV2):
    payload = {
        "type": "USER_GENERATED",
        "url": body.url,
        "context": body.context,
        "alt": body.user_alt
    }

    data_log.insert_one(payload)

    return {
        "status": "OK"
    }



@app.on_event("startup")
def on_startup():
    """
    Startup Function
    """
    print(f'[fastapi-init] Running FastAPI startup scripts')
    print(f'[fastapi-init] FastAPI Initialization was Completed!')

    


