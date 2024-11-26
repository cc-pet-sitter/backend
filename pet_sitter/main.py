#start server from root (backend) folder with "poetry run start"
from fastapi import FastAPI, HTTPException, Request, status, Depends # type: ignore
import uvicorn # type: ignore
from tortoise import Tortoise # type: ignore
from dotenv import load_dotenv # type: ignore
import os
import pet_sitter.models as models
import pet_sitter.basemodels as basemodels
import pet_sitter.seeds as seeds
import firebase_admin
from firebase_admin import credentials, auth
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from datetime import datetime

load_dotenv()

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
firebase_admin.initialize_app(cred)

app = FastAPI()

# Enable CORS for frontend interaction
origins = [
  os.getenv("FRONTEND_BASE_URL"),
  "http://localhost:5173",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Dependency for Firebase authentication
async def verify_firebase_token(request: Request):
  auth_header = request.headers.get("Authorization")
  if not auth_header:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Authorization header missing.",
          headers={"WWW-Authenticate": "Bearer"},
      )
  try:
      token_type, id_token = auth_header.split()
      if token_type.lower() != "bearer":
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Invalid authentication scheme.",
              headers={"WWW-Authenticate": "Bearer"},
          )
      decoded_token = auth.verify_id_token(id_token)
      return decoded_token
  except ValueError:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Invalid authorization header format.",
          headers={"WWW-Authenticate": "Bearer"},
      )
  except auth.InvalidIdTokenError:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Invalid ID token.",
          headers={"WWW-Authenticate": "Bearer"},
      )
  except Exception as e:
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Authentication error.",
          headers={"WWW-Authenticate": "Bearer"},
      )

@app.get("/") 
async def main_route():     
  return "Welcome to PetSitter!"

@app.post("/signup", status_code=201) 
async def sign_user_up(reqBody: basemodels.SignUpBody, decoded_token: dict = Depends(verify_firebase_token)):  
  # Verify that the email in the token matches the signup email
  if decoded_token.get('email') != reqBody.email:
      raise HTTPException(status_code=403, detail="Email mismatch.")
  
  # Check if user already exists in the database
  existing_user = await models.Appuser.filter(email=reqBody.email).first()
  if existing_user:
      raise HTTPException(status_code=400, detail="User already exists in the database.")

  # Create user in the database with firebase_user_id and more data
  appuser = await models.Appuser.create(
      **reqBody.dict(),
      firebase_user_id=decoded_token['uid']
  )
      
  if appuser:      
      return {"status":"ok", "user_id": appuser.id}
  else:
      raise HTTPException(status_code=500, detail='Failed to Add User')

@app.post("/login", status_code=200) 
async def log_user_in(decoded_token: dict = Depends(verify_firebase_token)):  
    # Extract email and uid from the decoded token
    email = decoded_token.get('email')
    uid = decoded_token.get('uid')
    
    if not email or not uid:
        raise HTTPException(status_code=400, detail="Invalid token data.")
    
    # Fetch user from the database
    user = await models.Appuser.filter(email=email, firebase_user_id=uid).first()
    if user:
        # Update last login timestamp
        user.last_login = datetime.now()
        await user.save()
    
        # Fetch other user data as needed
        return {
            "status": "ok",
            "user_id": user.id,
            "email": user.email,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "is_sitter": user.is_sitter,
            "profile_picture_src": user.profile_picture_src,
            # Add other fields as necessary
        }
    else:
        raise HTTPException(status_code=404, detail='User Not Found')
  
@app.get("/appuser/{id}", status_code=200) 
async def get_appuser_by_id(id: int):   
  appuser = await models.Appuser.filter(id=id).first() 

  if appuser:
    return appuser 
  else:
    raise HTTPException(status_code=404, detail=f'Appuser Not Found')

  
@app.put("/appuser/{id}", status_code=200) 
async def update_appuser_info(id: int, appuserReqBody: basemodels.UpdateAppuserBody, decoded_token: dict = Depends(verify_firebase_token)):  
  appuser = await models.Appuser.filter(id=id).first()
  
  if not appuser:
    raise HTTPException(status_code=404, detail='Appuser Not Found')
  
  if decoded_token['uid'] != appuser.firebase_user_id:
    raise HTTPException(status_code=403, detail="Not authorized to update this user.")

  await appuser.update_from_dict(appuserReqBody.dict(exclude_unset=True))
  await appuser.save()
  latestAppuser = await models.Appuser.get(id=id)
  return latestAppuser
  
@app.get("/sitter/{appuser_id}", status_code=200) 
async def get_sitter_by_appuser_id(appuser_id: int):   
  sitterArray = await models.Sitter.filter(appuser_id=appuser_id) 
  
  if sitterArray:
    return sitterArray[0] 
  else:
    raise HTTPException(status_code=404, detail=f'Sitter Not Found')

@app.post("/sitter/{appuser_id}", status_code=200) 
async def set_user_info(appuser_id: int, sitterReqBody: basemodels.SetSitterBody):  
  sitterArray = await models.Sitter.filter(appuser_id=appuser_id)

  if sitterArray: # the sitter already exists, so update it
    sitter = sitterArray[0]
    await sitter.update_from_dict(sitterReqBody.dict(exclude_unset=True))
    await sitter.save()
    latestSitter = await models.Sitter.get(appuser_id=appuser_id)
    return latestSitter
  else: #the sitter does not yet exist, so create it
    latestSitter = await models.Sitter.create(appuser_id=appuser_id, **sitterReqBody.dict())
    #update is_sitter on appuser
    userArray = await models.Appuser.filter(id=appuser_id)
    user = userArray[0]
    user.is_sitter = True
    await user.save()

    response = {}
    response["sitter"] = latestSitter
    response["appuser"] = user
    return response

@app.get("/appuser-extended/{id}", status_code=200) 
async def get_detailed_user_info_by_id(id: int):     
  appuserArray = await models.Appuser.filter(id=id) 
  
  if appuserArray:
    appuser = appuserArray[0]

    response = {}
    response["appuser"] = appuser

    sitterArray = await models.Sitter.filter(appuser_id=id)
    if sitterArray: #add the sitter record to the response
      sitter = sitterArray[0]
      response["sitter"] = sitter

    return response
  else:
    raise HTTPException(status_code=404, detail=f'User Not Found')

@app.post("/appuser-extended/{id}", status_code=200) 
async def set_user_info(id: int, appuserReqBody: basemodels.UpdateAppuserBody, sitterReqBody: basemodels.SetSitterBody | None = None):   
  appuserArray = await models.Appuser.filter(id=id) 
  
  if appuserArray:
    appuser = appuserArray[0]
    response = {}

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
        appuser.is_sitter = True #update is_sitter on appuser
    
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
async def get_all_matching_sitters(prefecture: str, city_ward: str | None = None, sitter_house_ok: bool | None = None, owner_house_ok: bool | None  = None, visit_ok: bool | None  = None, dogs_ok: bool | None  = None, cats_ok: bool | None  = None, fish_ok: bool | None  = None, birds_ok: bool | None  = None, rabbits_ok: bool | None  = None):     
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

      # appuser_search_conditions = {}
      # if prefecture:
      #   appuser_search_conditions["prefecture"] = True
      # if city_ward:
      #   appuser_search_conditions["city_ward"] = True

      matchingSitterArray = await models.Sitter.filter(**sitter_search_conditions).select_related("appuser").filter(appuser__prefecture=prefecture) ## Ex. Can use matchingSitterArray[0].appuser.email to get email from Appuser table for one user
      if matchingSitterArray:
        return matchingSitterArray
      else:
        raise HTTPException(status_code=404, detail=f'No Matching Sitters Found')

@app.get("/appuser/{id}/inquiry", status_code=200) 
async def get_all_relevant_inquiries_for_user(id: int, is_sitter: bool):
  if is_sitter:
      sitterInquiryArray = await models.Inquiry.filter(sitter_appuser_id=id)
      if sitterInquiryArray:
        return sitterInquiryArray
      else:
        raise HTTPException(status_code=404, detail=f'No Sitter Inquiries Found')
  else:
      ownerInquiryArray = await models.Inquiry.filter(owner_appuser_id=id)
      if ownerInquiryArray:
        return ownerInquiryArray
      else:
        raise HTTPException(status_code=404, detail=f'No Owner Inquiries Found')

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
  appusers = await models.Appuser.all()
  if not appusers:
    await seeds.seed_db()

@app.on_event("shutdown")
async def shutdown():
  # Close the Tortoise connection when shutting down the app
  await Tortoise.close_connections()

def start():
  """Launched with poetry run start at root level"""
  uvicorn.run("pet_sitter.main:app", port=8000, host="0.0.0.0", reload=True)