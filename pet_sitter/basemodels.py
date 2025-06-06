from pydantic import BaseModel # type: ignore
from datetime import datetime

class SignUpBody(BaseModel):
  email: str
  firstname: str
  lastname: str
  # firebase_user_id: str No need since the firebase user id comes from the token
  prefecture: str | None = None
  city_ward: str | None = None
  street_address: str | None = None
  postal_code: str | None = None

class LogInBody(BaseModel):
  email: str

class UpdateAppuserBody(BaseModel):
  firstname: str | None = None
  lastname: str | None = None
  email: str | None = None
  profile_picture_src: str | None = None
  prefecture: str | None = None
  city_ward: str | None = None
  street_address: str | None = None
  postal_code: str | None = None
  account_language: str | None = None
  english_ok: bool | None = None
  japanese_ok: bool | None = None
  average_user_rating: float | None = None
  user_profile_bio: str | None = None
  user_bio_picture_src_list: str | None = None

class SetSitterBody(BaseModel):
  sitter_profile_bio: str | None = None
  sitter_bio_picture_src_list: str | None = None
  sitter_house_ok: bool | None = None
  owner_house_ok: bool | None = None
  visit_ok: bool | None = None
  dogs_ok: bool | None = None
  cats_ok: bool | None = None
  fish_ok: bool | None = None
  birds_ok: bool | None = None
  rabbits_ok: bool | None = None

class CreateInquiryBody(BaseModel):
  owner_appuser_id: int
  sitter_appuser_id: int
  start_date: datetime
  end_date: datetime
  desired_service: str
  pet_id_list: str
  additional_info: str | None = None

class UpdateInquiryStatusBody(BaseModel):
  inquiry_status: str

class UpdateInquiryContentBody(BaseModel):
  start_date: datetime | None = None
  end_date: datetime | None = None
  desired_service: str | None = None
  pet_id_list: str | None = None
  additional_info: str | None = None

class CreateMessageBody(BaseModel):
  author_appuser_id: int
  recipient_appuser_id: int
  content: str

class CreateAvailabilityBody(BaseModel):
  available_date: datetime

class CreateReviewBody(BaseModel):
  author_appuser_id: int
  recipient_appuser_type: str
  comment: str | None = None
  score: int

class CreatePetBody(BaseModel):
  name: str
  type_of_animal: str
  subtype: str | None = None
  gender: str | None = None
  weight: float | None = None
  birthday: datetime | None = None
  known_allergies: str | None = None
  medications: str | None = None
  special_needs: str | None = None
  profile_picture_src: str | None = None
  pet_bio_picture_src_list: str | None = None
  profile_bio: str | None = None

class UpdatePetBody(BaseModel):
  name: str | None = None
  type_of_animal: str | None = None
  subtype: str | None = None
  gender: str | None = None
  weight: float | None = None
  birthday: datetime | None = None
  known_allergies: str | None = None
  medications: str | None = None
  special_needs: str | None = None
  profile_picture_src: str | None = None
  pet_bio_picture_src_list: str | None = None
  profile_bio: str | None = None

class FullAppuserResponseObject(BaseModel):
  id: int
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
  average_user_rating: float | None
  user_profile_bio: str | None
  user_bio_picture_src_list: str | None
  is_sitter: bool | None
  account_created: datetime | None
  last_updated: datetime | None
  last_login: datetime | None

  class Config:
    from_attributes = True

class ReducedAppuserResponseObject(BaseModel):
  id: int
  firstname: str | None
  lastname: str | None
  profile_picture_src: str | None
  prefecture: str | None
  city_ward: str | None
  postal_code: str | None
  account_language: str | None
  english_ok: bool | None
  japanese_ok: bool | None
  average_user_rating: float | None
  user_profile_bio: str | None
  user_bio_picture_src_list: str | None
  is_sitter: bool | None
  account_created: datetime | None
  last_updated: datetime | None
  last_login: datetime | None

  class Config:
    from_attributes = True