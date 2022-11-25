from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
def on_startup():
    """
    Startup Function
    """
    print(f'[fastapi-init] Running FastAPI startup scripts')
    print(f'[fastapi-init] FastAPI Initialization was Completed!')
