#start server from root (backend) folder with "poetry run start"
from fastapi import FastAPI, HTTPException # type: ignore
import uvicorn # type: ignore
from tortoise import Tortoise # type: ignore
from dotenv import load_dotenv # type: ignore
import os
import pet_sitter.models as models
import pet_sitter.basemodels as basemodels

load_dotenv()
app = FastAPI()   

@app.get("/") 
async def main_route():     
  return "Welcome to PetSitter!"

@app.post("/signup", status_code=201) 
async def sign_user_up(reqBody: basemodels.SignUpBody):  
  user = await models.Appuser.create(email=reqBody.email)
  if user:
    return {"status":"ok"}
  else:
    raise HTTPException(status_code=500, detail=f'Failed to Add User')

@app.post("/login", status_code=200) 
async def log_user_in(reqBody: basemodels.LogInBody):  
  userArray = await models.Appuser.filter(email=reqBody.email)
  if userArray:
    return userArray[0]
  else:
    raise HTTPException(status_code=404, detail=f'User Not Found')

@app.get("/appuser-extended/{id}", status_code=200) 
async def get_detailed_user_info_by_id(id: int):     
  return "Here is the appuser you asked for + BOTH owner AND sitter data!"

@app.post("/appuser-extended/{id}", status_code=200) 
async def set_user_info(id: int, user_type: str, appuserReqBody: basemodels.UpdateAppuserBody, sitterReqBody: basemodels.SetSitterBody | None = None, ownerReqBody: basemodels.SetOwnerBody | None = None):   
  appuserArray = await models.Appuser.filter(id=id) 
  
  if appuserArray:
    appuser = appuserArray[0]
    response = {}

    if user_type == "SITTER":
      if sitterReqBody:
        sitterArray = await models.Sitter.filter(appuser_id=id)

        if sitterArray: #update the retrieved sitter record
          sitter = sitterArray[0]
          await sitter.update_from_dict(sitterReqBody.dict(exclude_unset=True))
          await sitter.save()
          latestSitter = await models.Sitter.get(appuser_id=id)
          response["sitter"] = latestSitter
        else: #create a new sitter record
          latestSitter = await models.Sitter.create(appuser_id=id, **sitterReqBody.dict())  
          response["sitter"] = latestSitter
    elif  user_type == "OWNER":
      if ownerReqBody:
        ownerArray = await models.Owner.filter(appuser_id=id)

        if ownerArray: #update the retrieved owner record
          owner = ownerArray[0]
          await owner.update_from_dict(ownerReqBody.dict(exclude_unset=True))
          await owner.save()
          latestOwner = await models.Owner.get(appuser_id=id)
          response["owner"] = latestOwner
        else: #create a new owner record
            latestOwner = await models.Owner.create(appuser_id=id, **ownerReqBody.dict())  
            response["owner"] = latestOwner
    else:
      raise HTTPException(status_code=400, detail=f'No Valid User Type Received')
    
    #update the appuser record
    await appuser.update_from_dict(appuserReqBody.dict(exclude_unset=True))
    await appuser.save()
    latestAppuser = await models.Appuser.get(id=id)
    response["appuser"] = latestAppuser
    return response
  else:
    raise HTTPException(status_code=404, detail=f'User Does Not Exist')

#expects to receive the prefecture and city_ward of the user conducting the search + any booleans that are true (meaning the user want to find a sitter meeting those conditions)
@app.get("/appuser-sitters", status_code=200) 
async def get_all_matching_sitters(prefecture: str, city_ward: str, sitter_house_ok: bool | None = None, owner_house_ok: bool | None  = None, visit_ok: bool | None  = None, dogs_ok: bool | None  = None, cats_ok: bool | None  = None, fish_ok: bool | None  = None, birds_ok: bool | None  = None, rabbits_ok: bool | None  = None):     
      sitter_search_conditions = {}
      if sitter_house_ok:
        sitter_search_conditions["sitter_house_ok"] = True
      if owner_house_ok:
        sitter_search_conditions["owner_house_ok"] = True
      if visit_ok:
        sitter_search_conditions["visit_ok"] = True
      if dogs_ok:
        sitter_search_conditions["dogs_ok"] = True
      if cats_ok:
        sitter_search_conditions["cats_ok"] = True
      if fish_ok:
        sitter_search_conditions["fish_ok"] = True
      if birds_ok:
        sitter_search_conditions["birds_ok"] = True
      if rabbits_ok:
        sitter_search_conditions["rabbits_ok"] = True

      matchingSitterArray = await models.Sitter.filter(**sitter_search_conditions).select_related("appuser").filter(appuser__prefecture=prefecture, appuser__city_ward=city_ward) ## Ex. Can use matchingSitterArray[0].appuser.email to get email from Appuser table for one user
      if matchingSitterArray:
        return matchingSitterArray
      else:
        raise HTTPException(status_code=404, detail=f'No Matching Sitters Found')

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
    raise HTTPException(status_code=400, detail=f'No Valid User Type Received')

@app.get("/inquiry/{id}", status_code=200) 
async def get_inquiry_by_id(id: int):     
  inquiryArray = await models.Inquiry.filter(id=id)
  if inquiryArray:
    return inquiryArray[0]
  else:
    raise HTTPException(status_code=404, detail=f'Inquiry Not Found')

@app.post("/inquiry", status_code=201) 
async def create_inquiry(reqBody: basemodels.CreateInquiryBody):   
  inquiry = await models.Inquiry.create(**reqBody.dict())  
  if inquiry:
    return inquiry
  else:
    raise HTTPException(status_code=500, detail=f'Failed to Add Inquiry')

@app.patch("/inquiry/{id}", status_code=200) 
async def update_inquiry_status(id: int, reqBody: basemodels.UpdateInquiryStatusBody):  
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