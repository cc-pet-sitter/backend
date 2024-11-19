#start server from root (backend) folder with "poetry run start"
from fastapi import FastAPI # type: ignore
import uvicorn # type: ignore
from tortoise import Tortoise # type: ignore

app = FastAPI()   

@app.get("/") 
async def main_route():     
  return "Hello world!"

def start():
    """Launched with poetry run start at root level"""
    uvicorn.run("pet-sitter.main:app", port=8000, host="0.0.0.0", reload=True)