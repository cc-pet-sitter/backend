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

@app.post("/signup", status_code=201) 
async def sign_user_up(reqBody: SignUpBody):  
  user = await models.Appuser.create(email=reqBody.email)
  if user:
    return {"status":"ok"}
  else:
    raise HTTPException(status_code=500, detail=f'Failed to Add User')

@app.post("/login", status_code=200) 
async def log_user_in(reqBody: LogInBody):  
  userArray = await models.Appuser.filter(email=reqBody.email)
  if userArray:
    return userArray[0]
  else:
    raise HTTPException(status_code=404, detail=f'User Not Found')

@app.get("/appuser-extended/{id}", status_code=200) 
async def get_detailed_user_info_by_id(id: int):     
  return "Here is the appuser you asked for + owner and sitter data!"

@app.post("/appuser-extended/{id}", status_code=200) 
async def set_user_info(id: int, appuserReqBody: UpdateAppuserBody, sitterReqBody: SetSitterBody, ownerReqBody: SetOwnerBody):     
  #appuser = await
  return "Here is your updated appuser + owner and sitter data!"

# need to address prefecture and city_ward match
@app.get("/appuser-sitters", status_code=200) 
async def get_all_matching_sitters(sitter_house_ok: bool, owner_house_ok: bool, visit_ok: bool, dogs_ok: bool, cats_ok: bool, fish_ok: bool, birds_ok: bool, rabbits_ok: bool):     
      matchingSitterArray = await models.Sitter.filter(
        sitter_house_ok=sitter_house_ok, 
        owner_house_ok=owner_house_ok, 
        visit_ok=visit_ok, 
        dogs_ok=dogs_ok, 
        cats_ok=cats_ok, 
        fish_ok=fish_ok, 
        birds_ok=birds_ok, 
        rabbits_ok=rabbits_ok
        ).select_related("appuser") ## Ex. Can use matchingSitterArray[0].appuser.email to get email from Appuser table for one user
      if matchingSitterArray:
        return matchingSitterArray
      else:
        raise HTTPException(status_code=404, detail=f'No Sitters Found')

@app.get("/appuser/{id}/inquiry", status_code=200) 
async def get_all_relevant_inquiries_for_user(id: int, user_type: str):
  if user_type == "SITTER":
      sitterInquiryArray = await models.Inquiry.filter(sitter_appuser_id=id)
      if sitterInquiryArray:
        return sitterInquiryArray
      else:
        raise HTTPException(status_code=404, detail=f'No Sitter Inquiries Found')
  elif  user_type == "OWNER":
      ownerInquiryArray = await models.Inquiry.filter(owner_appuser_id=id)
      if ownerInquiryArray:
        return ownerInquiryArray
      else:
        raise HTTPException(status_code=404, detail=f'No Owner Inquiries Found')
  else:
    raise HTTPException(status_code=400, detail=f'No User Type Received')

@app.get("/inquiry/{id}", status_code=200) 
async def get_inquiry_by_id(id: int):     
  inquiryArray = await models.Inquiry.filter(id=id)
  if inquiryArray:
    return inquiryArray[0]
  else:
    raise HTTPException(status_code=404, detail=f'Inquiry Not Found')

@app.post("/inquiry", status_code=201) 
async def create_inquiry(reqBody: CreateInquiryBody):   
  inquiry = await models.Inquiry.create(**reqBody.dict())  
  if inquiry:
    return inquiry
  else:
    raise HTTPException(status_code=500, detail=f'Failed to Add Inquiry')

@app.patch("/inquiry/{id}", status_code=200) 
async def update_inquiry_status(id: int, reqBody: UpdateInquiryStatusBody):  
  inquiryArray = await models.Inquiry.filter(id=id) 
  if inquiryArray:
    inquiry = inquiryArray[0]
    inquiry.inquiry_status = reqBody.inquiry_status
    await inquiry.save()
    updatedInquiry = await models.Inquiry.get(id=id)
    return updatedInquiry
  else:
    raise HTTPException(status_code=404, detail=f'Inquiry Not Found')

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