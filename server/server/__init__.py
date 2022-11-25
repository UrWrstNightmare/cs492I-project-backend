import os
import uvicorn
from dotenv import load_dotenv

def start_uvicorn():
    load_dotenv()
    __port = os.getenv("PORT")
    __environment = os.getenv("ENVIRONMENT")
    __host = "0.0.0.0"

    __log_level = "debug" if __environment == "dev" else "info"
    __reload = True if __environment == "dev" else False

    print(f'[uvicorn-init] Initializing Uvicorn @ {__host + ":" + __port} (Log-Level: {__log_level}) (File-Watch: {__reload})')
    config = uvicorn.Config("server.main:app", port=int(__port), host=__host, log_level=__log_level, reload=__reload)
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    start_uvicorn()