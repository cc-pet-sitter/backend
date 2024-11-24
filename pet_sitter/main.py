#start server from root (backend) folder with "poetry run start"
from fastapi import FastAPI, HTTPException, status, Request, Depends
import uvicorn # type: ignore
from tortoise import Tortoise # type: ignore
from dotenv import load_dotenv # type: ignore
import os
import pet_sitter.models as models
import pet_sitter.basemodels as basemodels
import firebase_admin
from firebase_admin import credentials, auth
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime

TORTOISE_ORM = {
    "connections": {
        "default": os.getenv("DATABASE_URL")  
    },
    "apps": {
        "models": {
            "models": ["pet_sitter.models", "pet_sitter.basemodels"], 
            "default_connection": "default",
        },
    },
}

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

# Helper function to assign roles to Firebase Custom Claims
def set_custom_claims(uid: str, roles: List[str]):
    try:
        claims = {role: True for role in roles}
        auth.set_custom_user_claims(uid, claims)
    except auth.AuthError as e:
        # Log the error details for debugging
        print(f"AuthError when setting custom claims: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set custom claims.",
        )
    except Exception as e:
        # Log any other exceptions
        print(f"Unexpected error when setting custom claims: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set custom claims.",
        )

@app.get("/") 
async def main_route():     
  return "Welcome to PetSitter!"

from pet_sitter.basemodels import SignUpBody

@app.post("/signup", status_code=201) 
async def sign_user_up(reqBody: SignUpBody, decoded_token: dict = Depends(verify_firebase_token)):  
    # Verify that the email in the token matches the signup email
    if decoded_token.get('email') != reqBody.email:
        raise HTTPException(status_code=403, detail="Email mismatch.")

    # Check if user already exists in the database
    existing_user = await models.Appuser.filter(email=reqBody.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists in the database.")

    # Create user in the database with firebase_uid
    appuser = await models.Appuser.create(
        email=reqBody.email,
        firebase_uid=decoded_token['uid']
    )
    if appuser:
        roles_assigned = []
        if reqBody.role in {"owner", "both"}:
            # Create Owner profile
            owner = await models.Owner.create(
                appuser=appuser
            )
            roles_assigned.append("owner")
        if reqBody.role in {"sitter", "both"}:
            # Create Sitter profile
            sitter = await models.Sitter.create(
                appuser=appuser
            )
            roles_assigned.append("sitter")
        
        # Assign roles in Firebase if any
        if roles_assigned:
            set_custom_claims(decoded_token['uid'], roles_assigned)
        
        return {"status":"ok", "user_id": appuser.id}
    else:
        raise HTTPException(status_code=500, detail='Failed to Add User')

from pet_sitter.basemodels import LogInBody  # Ensure correct import

@app.post("/login", status_code=200) 
async def log_user_in(decoded_token: dict = Depends(verify_firebase_token)):  
    # Extract email and uid from the decoded token
    email = decoded_token.get('email')
    uid = decoded_token.get('uid')
    
    if not email or not uid:
        raise HTTPException(status_code=400, detail="Invalid token data.")
    
    # Fetch user from the database
    user = await models.Appuser.filter(email=email, firebase_uid=uid).first()
    if user:
        # Update last login timestamp
        user.last_login = datetime.now()
        await user.save()
    
        # Determine roles based on profiles
        roles = []
        if await user.owner_profile:
            roles.append("owner")
        if await user.sitter_profile:
            roles.append("sitter")
    
        # Fetch other user data as needed
        return {
            "status": "ok",
            "user_id": user.id,
            "email": user.email,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "roles": roles,
            "profile_picture_src": user.profile_picture_src,
            # Add other fields as necessary
        }
    else:
        raise HTTPException(status_code=404, detail='User Not Found')

@app.post("/assign-roles", status_code=200)
async def assign_roles(id: int, reqBody: basemodels.RoleAssignBody, decoded_token: dict = Depends(verify_firebase_token)):
    try:
        # Authorization: Only the user themselves or admin users can assign roles
        if decoded_token['uid'] != models.Appuser.get(id=id).firebase_uid and not decoded_token.get('admin', False):
            raise HTTPException(status_code=403, detail="Not authorized to assign roles.")
        
        # Validate roles
        valid_roles = {"owner", "sitter"}
        for role in reqBody.roles:
            if role not in valid_roles:
                raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
        
        # Fetch Appuser
        appuser = await models.Appuser.get_or_none(id=id)
        if not appuser:
            raise HTTPException(status_code=404, detail="User Not Found.")
        
        # Assign roles based on the request
        roles_assigned = []
        if "owner" in reqBody.roles and not await appuser.owner_profile:
            await models.Owner.create(appuser=appuser)
            roles_assigned.append("owner")
        if "sitter" in reqBody.roles and not await appuser.sitter_profile:
            await models.Sitter.create(appuser=appuser)
            roles_assigned.append("sitter")
        
        # Update Firebase Custom Claims
        if roles_assigned:
            set_custom_claims(decoded_token['uid'], roles_assigned)
        
        return {"message": "Roles assigned successfully."}
    except models.Appuser.DoesNotExist:
        raise HTTPException(status_code=404, detail="User Not Found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

    ownerArray = await models.Owner.filter(appuser_id=id)
    if ownerArray: #add the owner record to the response
      owner = ownerArray[0]
      response["owner"] = owner

    return response
  else:
    raise HTTPException(status_code=404, detail=f'User Not Found')

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