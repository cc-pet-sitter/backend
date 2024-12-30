#start server from root (backend) folder with "poetry run start"
from random import randint
from typing import List
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
import base64
import json

load_dotenv()

# Initialize Firebase Admin SDK
fb_cred_raw = json.loads(base64.b64decode(os.getenv("FIREBASE_CREDENTIALS")).decode())
fb_cred = credentials.Certificate(fb_cred_raw)

firebase_admin.initialize_app(fb_cred)

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
  return "Welcome to Mugi! むぎへようこそ！"

@app.post("/signup", status_code=201, responses={401: {"description": "Email mismatch."}, 400: {"description": "User already exists in the database."}, 500: {"description": "Failed to Add User"}}) 
async def sign_user_up(reqBody: basemodels.SignUpBody, decoded_token: dict = Depends(verify_firebase_token)):  
  # Verify that the email in the token matches the signup email
  if decoded_token.get('email') != reqBody.email:
      raise HTTPException(status_code=401, detail="Email mismatch.")
  
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
      return {"status":"ok", "appuser": appuser}
  else:
      raise HTTPException(status_code=500, detail='Failed to Add User')
  
def check_logged_in(decoded_token: dict):
    email = decoded_token.get('email')
    uid = decoded_token.get('uid')
    
    if not email or not uid: # no email or UID found in the token
        raise HTTPException(status_code=401, detail="Must Be Logged In")
    
def check_is_authorized(decoded_token: dict, requestedUserFirebaseID):
  if decoded_token['uid'] != requestedUserFirebaseID: # the calling user is not the same as the user whose properties are being targeted by the action
    raise HTTPException(status_code=403, detail="User Not Authorized")

async def check_is_authorized_for_inquiry(decoded_token: dict, ownerID, sitterID):
  uid = decoded_token.get('uid')
  appuser = await models.Appuser.filter(firebase_user_id=uid).first()

  if appuser.id != ownerID and appuser.id != sitterID: #the calling user is neither the inquiry's owner_appuser nor the inquiry's sitter_appuser
    raise HTTPException(status_code=403, detail="User Not Authorized")
    
@app.post("/login", status_code=200, responses={401: {"description": "Invalid token data."}, 404: {"description": "User Not Found"}}) 
async def log_user_in(decoded_token: dict = Depends(verify_firebase_token)):  
    # Extract email and uid from the decoded token
    email = decoded_token.get('email')
    uid = decoded_token.get('uid')
    
    if not email or not uid:
        raise HTTPException(status_code=401, detail="Invalid token data.")
    
    # Fetch user from the database
    user = await models.Appuser.filter(email=email, firebase_user_id=uid).first()
    if user:
        # Update last login timestamp
        user.last_login = datetime.now()
        await user.save()
    
        # Fetch other user data as needed
        return user
    else:
        raise HTTPException(status_code=404, detail='User Not Found')
  
@app.get("/appuser/{id}", status_code=200, responses={404: {"description": "Appuser Not Found"}}) 
async def get_appuser_by_id(id: int):   
  appuser = await models.Appuser.filter(id=id).first() 

  if appuser:
    return appuser 
  else:
    raise HTTPException(status_code=404, detail=f'Appuser Not Found')

  
@app.put("/appuser/{id}", status_code=200, responses={404: {"description": "Appuser Not Found"}, 403: {"description": "User Not Authorized"}}) 
async def update_appuser_info(id: int, appuserReqBody: basemodels.UpdateAppuserBody, decoded_token: dict = Depends(verify_firebase_token)):  
  appuser = await models.Appuser.filter(id=id).first()
  
  if not appuser:
    raise HTTPException(status_code=404, detail='Appuser Not Found')
  
  check_is_authorized(decoded_token, appuser.firebase_user_id)

  await appuser.update_from_dict(appuserReqBody.dict(exclude_unset=True))
  await appuser.save()
  latestAppuser = await models.Appuser.get(id=id)
  return latestAppuser
  
@app.get("/sitter/{appuser_id}", status_code=200, responses={404: {"description": "Sitter Not Found"}}) 
async def get_sitter_by_appuser_id(appuser_id: int):   
  sitter = await models.Sitter.filter(appuser_id=appuser_id).first()
  
  if sitter:
    return sitter
  else:
    raise HTTPException(status_code=404, detail=f'Sitter Not Found')

@app.post("/sitter/{appuser_id}", status_code=200, responses={403: {"description": "User Not Authorized"}, 400: {"description": "sitter_profile_bio is Mandatory"}}) 
async def set_user_info(appuser_id: int, sitterReqBody: basemodels.SetSitterBody, decoded_token: dict = Depends(verify_firebase_token)):  
  sitter = await models.Sitter.filter(appuser_id=appuser_id).first()

  appuser = await models.Appuser.filter(id=appuser_id).first()
  check_is_authorized(decoded_token, appuser.firebase_user_id)

  if sitter: # the sitter already exists, so update it
    await sitter.update_from_dict(sitterReqBody.dict(exclude_unset=True))
    await sitter.save()
    latestSitter = await models.Sitter.get(appuser_id=appuser_id)
    return latestSitter
  elif sitterReqBody.sitter_profile_bio: #the sitter does not yet exist, so create it
    latestSitter = await models.Sitter.create(appuser_id=appuser_id, **sitterReqBody.dict(exclude_unset=True))
    #update is_sitter on appuser
    user = await models.Appuser.filter(id=appuser_id).first()
    user.is_sitter = True
    await user.save()

    response = {}
    response["sitter"] = latestSitter
    response["appuser"] = user
    return response
  else:
    raise HTTPException(status_code=400, detail=f'sitter_profile_bio is Mandatory')

@app.get("/appuser-extended/{id}", status_code=200, responses={404: {"description": "User Not Found"}}) 
async def get_detailed_user_info_by_id(id: int):     
  appuser = await models.Appuser.filter(id=id).first()
  
  if appuser:
    response = {}
    response["appuser"] = appuser

    sitter = await models.Sitter.filter(appuser_id=id).first()
    if sitter: #add the sitter record to the response
      response["sitter"] = sitter

    return response
  else:
    raise HTTPException(status_code=404, detail=f'User Not Found')

def validate_pet_fields(type_of_animal: str, weight: float, gender: str):
  if type_of_animal and type_of_animal not in ["dog", "cat", "bird", "fish", "rabbit"]:
    raise HTTPException(status_code=400, detail=f'type_of_animal should be "dog", "cat", "bird", "fish", or "rabbit"')
  
  if weight and weight <= 0:
    raise HTTPException(status_code=400, detail=f'"weight" should be a positive number')
  
  if gender and gender not in ["male", "female"]:
    raise HTTPException(status_code=400, detail=f'Pet gender should be "male" or "female"')

@app.post("/appuser/{appuser_id}/pet", status_code=201, responses={403: {"description": "User Not Authorized"}, 400: {"description": "Invalid Type of Animal, Invalid Pet Gender, or Weight is Nonpositive"}, 404: {"description": "User Does Not Exist"}, 500: {"description": "Failed to Add Pet"}}) 
async def create_pet_profile(appuser_id: int, reqBody: basemodels.CreatePetBody, decoded_token: dict = Depends(verify_firebase_token)):  
  appuser = await models.Appuser.filter(id=appuser_id).first()

  if not appuser:
    raise HTTPException(status_code=404, detail=f'User Does Not Exist')
  
  check_is_authorized(decoded_token, appuser.firebase_user_id)
  validate_pet_fields(reqBody.type_of_animal, reqBody.weight, reqBody.gender)

  newPet = await models.Pet.create(appuser_id=appuser_id, **reqBody.dict(exclude_unset=True))

  if newPet:
    return newPet
  else:
    raise HTTPException(status_code=500, detail=f'Failed to Add Pet')
  
@app.put("/pet/{id}", status_code=200, responses={403: {"description": "User Not Authorized"}, 400: {"description": "Invalid Type of Animal, Invalid Pet Gender, or Weight is Nonpositive"}, 404: {"description": "Pet Not Found"}, 500: {"description": "Failed to Update Pet Profile"}}) 
async def update_pet_profile(id: int, reqBody: basemodels.UpdatePetBody, decoded_token: dict = Depends(verify_firebase_token)):  
  pet = await models.Pet.filter(id=id).first()

  if not pet:
    raise HTTPException(status_code=404, detail=f'Pet Not Found')
  
  appuser = await models.Appuser.filter(id=pet.appuser_id).first()
  check_is_authorized(decoded_token, appuser.firebase_user_id)

  validate_pet_fields(reqBody.type_of_animal, reqBody.weight, reqBody.gender)

  await pet.update_from_dict(reqBody.dict(exclude_unset=True))
  await pet.save()

  updatedPet = await models.Pet.filter(id=id).first()

  if updatedPet:
    return updatedPet
  else:
    raise HTTPException(status_code=500, detail=f'Failed to Update Pet Profile')
  
@app.get("/appuser/{appuser_id}/pet", status_code=200, responses={400: {"description": "Invalid Request"}, 403: {"description": "User Not Authorized"}, 404: {"description": "User Does Not Exist"}}) 
async def get_all_pets_for_user(appuser_id: int, decoded_token: dict = Depends(verify_firebase_token), inquiry_id: int | None = None): 
  appuser = await models.Appuser.filter(id=appuser_id).first()

  if not appuser:
    raise HTTPException(status_code=404, detail=f'User Does Not Exist')
  
  if not inquiry_id:
    check_is_authorized(decoded_token, appuser.firebase_user_id)
  else: # for when a sitter needs to access an owner's pet data on their shared inquiry
    inquiry = await models.Inquiry.filter(id=inquiry_id).first()

    if not inquiry or inquiry.owner_appuser_id != appuser_id: # ensure that the owner data being requested matches the owner of the inquiry
      raise HTTPException(status_code=400, detail=f'Invalid Request')
    
    await check_is_authorized_for_inquiry(decoded_token, inquiry.owner_appuser_id, inquiry.sitter_appuser_id)

  userPetsArray = await models.Pet.filter(appuser_id=appuser_id).order_by('id') # to stabilize display order when pet profiles are updated
  if userPetsArray:
    return userPetsArray
  else:
    return []
  
@app.get("/pet/{id}", status_code=200, responses={404: {"description": "Pet Not Found"}}) 
async def get_pet_by_id(id: int): 
  pet = await models.Pet.filter(id=id).first()

  if not pet:
    raise HTTPException(status_code=404, detail=f'Pet Not Found')
  
  return pet

@app.get("/pet", status_code=200) 
async def get_all_pets(numOfPets: int = 500): 
  petsPerPage = numOfPets
  totalPets = await models.Pet.all().count()
  totalPages = totalPets // petsPerPage
  randomPage = randint(0, totalPages - 1)
  offset = randomPage * petsPerPage

  petsArray = await models.Pet.all().limit(numOfPets).offset(offset) # limit the results to a random subset of all pets

  if petsArray:
    return petsArray
  else:
    return []
  
@app.delete("/pet/{id}", status_code=200, responses={403: {"description": "User Not Authorized"}, 500: {"description": "Failed to Delete Pet Profile"}}) 
async def delete_pet_by_id(id: int, decoded_token: dict = Depends(verify_firebase_token)): 
  try:
    pet = await models.Pet.get(id=id)
    appuser = await models.Appuser.get(id=pet.appuser_id)
    check_is_authorized(decoded_token, appuser.firebase_user_id)
    await pet.delete()
    return f'Pet profile #{id} has been deleted'
  except Exception as e:
    raise HTTPException(status_code=500, detail=f'Failed to Delete Pet Profile: {str(e)}')

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

      appuser_search_conditions = {}
      appuser_search_conditions["appuser__prefecture"] = prefecture
      
      if city_ward:
        appuser_search_conditions["appuser__city_ward"] = city_ward

      matchingSitterArray = await models.Sitter.filter(**sitter_search_conditions).select_related("appuser").filter(**appuser_search_conditions) ## Ex. Can use matchingSitterArray[0].appuser.email to get email from Appuser table for one user

      if matchingSitterArray:
        responseArray = []

        for matchingSitter in matchingSitterArray:
          sitterAppuserPair = {}
          sitterAppuserPair["sitter"] = matchingSitter
          sitterAppuserPair["appuser"] = matchingSitter.appuser
          responseArray.append(sitterAppuserPair)
          
        return responseArray
      else:
        return []

@app.get("/appuser/{id}/inquiry", status_code=200, responses={403: {"description": "User Not Authorized"}}) 
async def get_all_relevant_inquiries_for_user(id: int, is_sitter: bool, decoded_token: dict = Depends(verify_firebase_token)):
  appuser = await models.Appuser.filter(id=id).first()

  check_is_authorized(decoded_token, appuser.firebase_user_id)

  if is_sitter:
      sitterInquiryArray = await models.Inquiry.filter(sitter_appuser_id=id).order_by('id')
      if sitterInquiryArray:
        return sitterInquiryArray
      else:
        return []
  else:
      ownerInquiryArray = await models.Inquiry.filter(owner_appuser_id=id).order_by('id')
      if ownerInquiryArray:
        return ownerInquiryArray
      else:
        return []

@app.get("/inquiry/{id}", status_code=200, responses={403: {"description": "User Not Authorized"}, 404: {"description": "Inquiry Not Found"}}) 
async def get_inquiry_by_id(id: int, decoded_token: dict = Depends(verify_firebase_token)):     
  inquiry = await models.Inquiry.filter(id=id).first()
  if inquiry:
    await check_is_authorized_for_inquiry(decoded_token, inquiry.owner_appuser_id, inquiry.sitter_appuser_id)
    return inquiry
  else:
    raise HTTPException(status_code=404, detail=f'Inquiry Not Found')

@app.post("/inquiry", status_code=201, responses={403: {"description": "User Not Authorized"}, 404: {"description": "Failed to Add Inquiry"}}) 
async def create_inquiry(reqBody: basemodels.CreateInquiryBody, decoded_token: dict = Depends(verify_firebase_token)):
  appuser = await models.Appuser.get(id=reqBody.owner_appuser_id)
  check_is_authorized(decoded_token, appuser.firebase_user_id)
  try:
    inquiry = await models.Inquiry.create(**reqBody.dict())     
    return inquiry
  except Exception as e:
    raise HTTPException(status_code=500, detail=f'Failed to Add Inquiry: {str(e)}')

@app.patch("/inquiry/{id}", status_code=200, responses={403: {"description": "User Not Authorized"}, 400: {"description": "Invalid Status Received or Inquiry Already Finalized"}, 404: {"description": "Inquiry Not Found"}}) 
async def update_inquiry_status(id: int, reqBody: basemodels.UpdateInquiryStatusBody, decoded_token: dict = Depends(verify_firebase_token)):  
  if reqBody.inquiry_status not in ["approved", "rejected"]:
    raise HTTPException(status_code=400, detail=f'Invalid Status Received')

  inquiry = await models.Inquiry.filter(id=id).first()

  if inquiry:
    await check_is_authorized_for_inquiry(decoded_token, inquiry.owner_appuser_id, inquiry.sitter_appuser_id)

    if inquiry.inquiry_status not in [models.InquiryStatus.REQUESTED]:
       raise HTTPException(status_code=400, detail=f'Inquiry Already Finalized')

    inquiry.inquiry_status = reqBody.inquiry_status
    inquiry.inquiry_finalized = datetime.now()
    await inquiry.save()
    updatedInquiry = await models.Inquiry.get(id=id)
    return updatedInquiry
  else:
    raise HTTPException(status_code=404, detail=f'Inquiry Not Found')

@app.put("/inquiry/{id}", status_code=200, responses={403: {"description": "User Not Authorized"}, 404: {"description": "Inquiry Not Found"}}) 
async def update_inquiry_content(id: int, reqBody: basemodels.UpdateInquiryContentBody, decoded_token: dict = Depends(verify_firebase_token)):  
  inquiry = await models.Inquiry.filter(id=id).first()

  if inquiry:
    await check_is_authorized_for_inquiry(decoded_token, inquiry.owner_appuser_id, inquiry.sitter_appuser_id)
    await inquiry.update_from_dict(reqBody.dict(exclude_unset=True))
    await inquiry.save()
    updatedInquiry = await models.Inquiry.get(id=id)
    return updatedInquiry
  else:
    raise HTTPException(status_code=404, detail=f'Inquiry Not Found')
  
@app.post("/inquiry/{id}/message", status_code=201, responses={403: {"description": "User Not Authorized"}, 500: {"description": "Failed to Add Message"}}) 
async def create_message(id: int, reqBody: basemodels.CreateMessageBody, decoded_token: dict = Depends(verify_firebase_token)):
  try:
    inquiry = await models.Inquiry.filter(id=id).first()
    await check_is_authorized_for_inquiry(decoded_token, inquiry.owner_appuser_id, inquiry.sitter_appuser_id)
    message = await models.Message.create(inquiry_id=id, **reqBody.dict())
    return message
  except Exception as e:
    raise HTTPException(status_code=500, detail=f'Failed to Add Message: {str(e)}')
  
@app.get("/inquiry/{id}/message", status_code=200, responses={403: {"description": "User Not Authorized"}, 404: {"description": "Inquiry Does Not Exist"}}) 
async def get_all_messages_from_inquiry(id: int, decoded_token: dict = Depends(verify_firebase_token)):
  inquiry = await models.Inquiry.filter(id=id).first()

  if not inquiry:
    raise HTTPException(status_code=404, detail=f'Inquiry Does Not Exist')

  await check_is_authorized_for_inquiry(decoded_token, inquiry.owner_appuser_id, inquiry.sitter_appuser_id)

  inquiryMessagesArray = await models.Message.filter(inquiry_id=id)
  if inquiryMessagesArray:
    return inquiryMessagesArray
  else:
    return []
  
@app.get("/inquiry/{id}/pet", status_code=200, responses={403: {"description": "User Not Authorized"}, 404: {"description": "Inquiry Does Not Exist"}}) 
async def get_all_pets_from_inquiry(id: int, decoded_token: dict = Depends(verify_firebase_token)):
  inquiry = await models.Inquiry.filter(id=id).first()

  if inquiry:
    await check_is_authorized_for_inquiry(decoded_token, inquiry.owner_appuser_id, inquiry.sitter_appuser_id)

    petsCSVStr = inquiry.pet_id_list

    if petsCSVStr:
      petIDList = petsCSVStr.split(",")
      response = {}
      response["pets_not_found"] = ""
      response["pets_array"] = []
      petsArray = []

      for i in range(len(petIDList)):
        try:
          petObject = await get_pet_by_id(petIDList[i])
          
          if petObject:
            petsArray.append(petObject)
        except:
            if not response["pets_not_found"]:
              response["pets_not_found"] += petIDList[i]
            else:
              response["pets_not_found"] += ","+ petIDList[i]
      
      if petsArray:
        response["pets_array"] = petsArray

      return response

  else:
    raise HTTPException(status_code=404, detail=f'Inquiry Does Not Exist')
      
@app.post("/appuser/{id}/availability", status_code=201, responses={403: {"description": "User Not Authorized"}, 500: {"description": "Failed to Add Availability"}}) 
async def create_availabilities(id: int, reqBody: List[basemodels.CreateAvailabilityBody], decoded_token: dict = Depends(verify_firebase_token)):
  appuser = await models.Appuser.filter(id=id).first()
  check_is_authorized(decoded_token, appuser.firebase_user_id)

  responseArray = []
  
  for i in range(len(reqBody)):
    availability = await models.Availability.filter(appuser_id=id, available_date=reqBody[i].available_date).first()
    if not availability:
      try:
        newAvailability = await models.Availability.create(appuser_id=id, **reqBody[i].dict())
        responseArray.append(newAvailability)
      except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to Add Availability: {str(e)}')
    
  return responseArray
  
@app.delete("/availability/{id}", status_code=200, responses={403: {"description": "User Not Authorized"}, 500: {"description": "Failed to Delete Availability"}})
async def delete_availability(id: int, decoded_token: dict = Depends(verify_firebase_token)):
  try:
    availability = await models.Availability.get(id=id)
    appuser = await models.Appuser.filter(id=availability.appuser_id).first()
    check_is_authorized(decoded_token, appuser.firebase_user_id)
    await availability.delete()
    return f'Availabilty #{id} has been deleted'
  except Exception as e:
    raise HTTPException(status_code=500, detail=f'Failed to Delete Availability: {str(e)}')

@app.get("/appuser/{id}/availability", status_code=200, responses={400: {"description": "The User is Not a Sitter"}})
async def get_all_availabilities_for_sitter(id: int):
  appuser = await models.Appuser.get(id=id)

  if appuser.is_sitter:
    sitterAvailabilitiesArray = await models.Availability.filter(appuser_id=id)
    if sitterAvailabilitiesArray:
      return sitterAvailabilitiesArray
    else:
      return []
  else:
    raise HTTPException(status_code=400, detail=f'The User is Not a Sitter')
  
@app.post("/appuser/{id}/review", status_code=201, responses={401: {"description": "Must Be Logged In"}, 400: {"description": "Invalid Recipient Appuser Type or Review Score Not 1-5"}, 404: {"description": "User(s) Not Found"}, 500: {"description": "Failed to Add Review"}}) 
async def create_review(id: int, reqBody: basemodels.CreateReviewBody, decoded_token: dict = Depends(verify_firebase_token)):
  check_logged_in(decoded_token)

  if reqBody.recipient_appuser_type not in ["sitter", "owner"]:
    raise HTTPException(status_code=400, detail=f'recipient_appuser_type should be about "owner" or about "sitter"')
  
  if reqBody.score > 5 or reqBody.score < 1:
    raise HTTPException(status_code=400, detail=f'"score" should be an integer between 1 and 5')
  
  recipient = await models.Appuser.get(id=id)
  author = await models.Appuser.get(id=reqBody.author_appuser_id)

  if not recipient or not author:
    raise HTTPException(status_code=404, detail=f'Author and/or Recipient User Not Found')

  response = {}

  try:
    review = await models.Review.create(recipient_appuser_id=id, **reqBody.dict())
    response["review"] = review

    if not recipient.average_user_rating:
      recipient.average_user_rating = review.score
      await recipient.save()
      response["appuser"] = recipient
    else:
      reviewArray = await get_all_reviews_for_user(id)
      reviewCount = len(reviewArray)
      scoreSum = 0

      for i in range(reviewCount):
        scoreSum += reviewArray[i].score

      recipient.average_user_rating = scoreSum / reviewCount
      await recipient.save()
      response["appuser"] = recipient

    return response
  except Exception as e:
    raise HTTPException(status_code=500, detail=f'Failed to Add Review: {str(e)}')
  
@app.get("/appuser/{id}/review", status_code=200, responses={404: {"description": "User Not Found"}}) 
async def get_all_reviews_for_user(id: int, recipient_appuser_type: str | None = None):
  appuser = await models.Appuser.get(id=id)

  if not appuser:
    raise HTTPException(status_code=404, detail=f'User Not Found')

  appuserReviewsArray = []

  if recipient_appuser_type == "owner" or recipient_appuser_type == "sitter":
    appuserReviewsArray = await models.Review.filter(recipient_appuser_id=id, recipient_appuser_type=recipient_appuser_type)
  else:
    appuserReviewsArray = await models.Review.filter(recipient_appuser_id=id)

  if appuserReviewsArray:
    return appuserReviewsArray
  else:
    return []

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