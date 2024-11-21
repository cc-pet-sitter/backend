#start server from root (backend) folder with "poetry run start"
from fastapi import FastAPI 
import uvicorn 
from tortoise import Tortoise 
from pydantic import BaseModel 
from dotenv import load_dotenv
import os
import pet_sitter.models as models
# DATABASE_URL = "postgres://postgres:codechrysalis@localhost:5432/petsitter"

load_dotenv()
app = FastAPI()   

print(os.getenv("DATABASE_URL"))

@app.get("/") 
async def main_route():     
  return "Welcome to PetSitter!"

@app.post("/signup") 
async def sign_user_up():  
  user = await models.Appuser.create()
  # return "Thanks for signing up!"
  return {"status":"ok"}

@app.post("/login") 
async def log_user_in():     
  return "Thanks for logging in!"

@app.get("/appuser-extended/{id}") 
async def get_detailed_user_info_by_id(id: int):     
  return "Here is the appuser you asked for + owner and sitter data!"

@app.post("/appuser-extended/{id}") 
async def set_user_info(id: int):     
  return "Here is your updated appuser + owner and sitter data!"

@app.get("/appuser-sitters") 
async def get_all_matching_sitters(sitter_house_ok: bool, owner_house_ok: bool, visit_ok: bool, dogs_ok: bool, cats_ok: bool, fish_ok: bool, birds_ok: bool, rabbits_ok: bool):     
  return "All these sitters are available to help!"

@app.get("/appuser/{id}/inquiry") 
async def get_all_relevant_inquiries_for_user(id: int):     
  return "These are the inquiries for your user role!"

@app.get("/inquiry/{id}") 
async def get_inquiry_by_id(id: int):     
  return "Here is the inquiry you asked for!"

@app.post("/inquiry") 
async def create_inquiry():     
  return "Here is your new inquiry request!"

@app.patch("/inquiry/{id}") 
async def update_inquiry_status(id: int):     
  return "Inquiry status updated as requested!"

@app.on_event("startup")
async def startup():
    # Initialize Tortoise ORM with the database connection
    await Tortoise.init(db_url=os.getenv("DATABASE_URL"), modules={"models": ["pet-sitter.models"]})
    await Tortoise.generate_schemas()

@app.on_event("shutdown")
async def shutdown():
    # Close the Tortoise connection when shutting down the app
    await Tortoise.close_connections()

def start():
    """Launched with poetry run start at root level"""
    uvicorn.run("pet-sitter.main:app", port=8000, host="0.0.0.0", reload=True)