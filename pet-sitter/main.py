#start server from root (backend) folder with "poetry run start"
from fastapi import FastAPI
import uvicorn

app = FastAPI()   

@app.get("/") 
async def main_route():     
  return "Hello world!"