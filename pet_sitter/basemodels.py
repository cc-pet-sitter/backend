from pydantic import BaseModel # type: ignore
from datetime import datetime

class SignUpBody(BaseModel):
  email: str

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

class SetSitterBody(BaseModel):
  average_sitter_rating: float | None = None
  profile_bio: str | None = None
  bio_picture_src_list: str | None = None
  sitter_house_ok: bool | None = None
  owner_house_ok: bool | None = None
  visit_ok: bool | None = None
  dogs_ok: bool | None = None
  cats_ok: bool | None = None
  fish_ok: bool | None = None
  birds_ok: bool | None = None
  rabbits_ok: bool | None = None

class SetOwnerBody(BaseModel):
  average_owner_rating: float | None = None
  profile_bio: str | None = None
  bio_picture_src_list: str | None = None

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