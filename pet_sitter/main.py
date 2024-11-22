#start server from root (backend) folder with "poetry run start"
from fastapi import FastAPI, HTTPException
import uvicorn 
from tortoise import Tortoise 
from pydantic import BaseModel 
from dotenv import load_dotenv
import os
import pet_sitter.models as models
from datetime import datetime

load_dotenv()
app = FastAPI()   

class SignUpBody(BaseModel):
  email: str

class LogInBody(BaseModel):
  email: str

class UpdateAppuserBody(BaseModel):
  firstname: str | None
  lastname: str | None
  email: str | None
  profile_picture_src: str | None
  prefecture: str | None
  city_ward: str | None
  street_address: str | None
  postal_code: str | None
  account_language: str | None
  english_ok: bool | None
  japanese_ok: bool | None

class SetSitterBody(BaseModel):
  average_sitter_rating: float | None
  profile_bio: str | None
  bio_picture_src_list: str | None
  sitter_house_ok: bool | None
  owner_house_ok: bool | None
  dogs_ok: bool | None
  cats_ok: bool | None
  fish_ok: bool | None
  birds_ok: bool | None
  rabbits_ok: bool | None
  appuser_id: int

class SetOwnerBody(BaseModel):
  average_sitter_rating: float | None
  profile_bio: str | None
  bio_picture_src_list: str | None
  appuser_id: int

class CreateInquiryBody(BaseModel):
  owner_appuser_id: int
  sitter_appuser_id: int
  start_date: datetime
  end_date: datetime
  desired_service: str
  pet_id_list: str
  additional_info: str | None

class UpdateInquiryStatusBody(BaseModel):
  inquiry_status: str

@app.get("/") 
async def main_route():     
  return "Welcome to PetSitter!"

@app.post("/signup") 
async def sign_user_up(reqBody: SignUpBody):  
  await models.Appuser.create(email=reqBody.email)
  return {"status":"ok"}

@app.post("/login") 
async def log_user_in(reqBody: LogInBody):  
  userArray = await models.Appuser.filter(email=reqBody.email)
  return userArray[0]

@app.get("/appuser-extended/{id}") 
async def get_detailed_user_info_by_id(id: int):     
  return "Here is the appuser you asked for + owner and sitter data!"

@app.post("/appuser-extended/{id}") 
async def set_user_info(id: int, appuserReqBody: UpdateAppuserBody, sitterReqBody: SetSitterBody, ownerReqBody: SetOwnerBody):     
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
async def create_inquiry(reqBody: CreateInquiryBody):   
  inquiry = await models.Inquiry.create(**reqBody.dict())  
  if inquiry:
    return inquiry
  else:
    raise HTTPException(status_code=404, detail=f'Failed to add the inquiry')

@app.patch("/inquiry/{id}") 
async def update_inquiry_status(id: int):     
  return "Inquiry status updated as requested!"

@app.on_event("startup")
async def startup():
    # Initialize Tortoise ORM with the database connection
    await Tortoise.init(db_url=os.getenv("DATABASE_URL"), modules={"models": ["pet_sitter.models"]})
    await Tortoise.generate_schemas()

@app.on_event("shutdown")
async def shutdown():
    # Close the Tortoise connection when shutting down the app
    await Tortoise.close_connections()

def start():
    """Launched with poetry run start at root level"""
    uvicorn.run("pet_sitter.main:app", port=8000, host="0.0.0.0", reload=True)