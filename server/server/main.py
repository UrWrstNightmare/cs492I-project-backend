from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import HttpUrl, BaseModel, Field

from fastapi.logger import logger

from transformers import pipeline
import torch

from PIL import Image
import requests
from io import BytesIO

app = FastAPI()

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

@app.post("/api/v1/predict")
async def predict(body: PredictionInput):
    logger.info(f"[API][PREDICT] API Called")
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


    

@app.on_event("startup")
def on_startup():
    """
    Startup Function
    """
    print(f'[fastapi-init] Running FastAPI startup scripts')
    print(f'[fastapi-init] FastAPI Initialization was Completed!')
