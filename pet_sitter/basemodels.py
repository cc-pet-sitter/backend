from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

# Updated SignUpBody with role selection and validation
class SignUpBody(BaseModel):
    email: str
    role: Optional[str] = None  # "owner", "sitter", or "both"

    @validator('role')
    def validate_role(cls, v):
        if v:
            valid_roles = {"owner", "sitter", "both"}
            if v.lower() not in valid_roles:
                raise ValueError(f"Role must be one of {valid_roles}.")
            return v.lower()
        return v

class LogInBody(BaseModel):
    email: str
    password: str  # Implement password verification if needed

class UpdateAppuserBody(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    profile_picture_src: Optional[str] = None
    prefecture: Optional[str] = None
    city_ward: Optional[str] = None
    street_address: Optional[str] = None
    postal_code: Optional[str] = None
    account_language: Optional[str] = None
    english_ok: Optional[bool] = None
    japanese_ok: Optional[bool] = None

class SetSitterBody(BaseModel):
    average_sitter_rating: Optional[float] = None
    profile_bio: Optional[str] = None
    bio_picture_src_list: Optional[str] = None
    sitter_house_ok: Optional[bool] = None
    owner_house_ok: Optional[bool] = None
    dogs_ok: Optional[bool] = None
    cats_ok: Optional[bool] = None
    fish_ok: Optional[bool] = None
    birds_ok: Optional[bool] = None
    rabbits_ok: Optional[bool] = None
    appuser_id: int

class SetOwnerBody(BaseModel):
    average_sitter_rating: Optional[float] = None
    profile_bio: Optional[str] = None
    bio_picture_src_list: Optional[str] = None
    appuser_id: int

class CreateInquiryBody(BaseModel):
    owner_appuser_id: int
    sitter_appuser_id: int
    start_date: datetime
    end_date: datetime
    desired_service: str
    pet_id_list: str
    additional_info: Optional[str] = None

class UpdateInquiryStatusBody(BaseModel):
    inquiry_status: str

class RoleAssignBody(BaseModel):
    roles: List[str]  # e.g., ["owner", "sitter"]