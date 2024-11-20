from tortoise import fields, models # type: ignore
from enum import Enum

class InquiryStatus(Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"

class AnimalType(Enum):
  DOG = "dog"
  CAT = "cat"
  FISH = "fish"
  RABBIT = "rabbit"
  BIRD = "bird"

class UserType(Enum):
  OWNER = "owner"
  SITTER = "sitter"

class PetServices(Enum):
  OWNER_HOUSE = "owner_house"
  SITTER_HOUSE = "sitter_house"
  VISIT = "visit"

class AccountLanguage(Enum):
  ENGLISH = "english"
  JAPANESE = "japanese"

class Appuser(models.Model):
  id = fields.IntField(primary_key=True)
  firstname = fields.CharField(max_length=40)
  lastname = fields.CharField(max_length=40)
  email = fields.CharField(unique=True, max_length=40)
  account_created = fields.DatetimeField(auto_now_add=True)
  last_updated = fields.DatetimeField(auto_now=True)
  last_login = fields.DatetimeField(null=True)
  profile_picture_src = fields.CharField(null=True, max_length=120)
  prefecture = fields.CharField(null=True, max_length=40)
  city_ward = fields.CharField(null=True, max_length=40)
  street_address = fields.CharField(null=True, max_length=40)
  postal_code = fields.CharField(null=True, max_length=40)
  account_language = fields.CharEnumField(AccountLanguage, default=AccountLanguage.ENGLISH)
  english_ok = fields.BooleanField(default=False)
  japanese_ok = fields.BooleanField(default=False)
  owner_id = fields.ForeignKeyField("models.Owner", related_name="appusers", null=True)
  sitter_id = fields.ForeignKeyField("models.Sitter", related_name="appusers", null=True)

class Owner(models.Model):
  id = fields.IntField(primary_key=True)
  average_owner_rating = fields.FloatField(null=True)
  profile_bio = fields.TextField(null=True)
  bio_picture_src_list = fields.TextField(null=True)

class Sitter(models.Model):
  id = fields.IntField(primary_key=True)
  average_sitter_rating = fields.FloatField(null=True)
  profile_bio = fields.TextField(null=True)
  bio_picture_src_list = fields.TextField(null=True)
  sitter_house_ok = fields.BooleanField(default=False)
  owner_house_ok = fields.BooleanField(default=False)
  visit_ok = fields.BooleanField(default=False)
  dogs_ok = fields.BooleanField(default=False)
  cats_ok = fields.BooleanField(default=False)
  fish_ok = fields.BooleanField(default=False)
  birds_ok = fields.BooleanField(default=False)
  rabbits_ok = fields.BooleanField(default=False)
  
class Pet(models.Model):
  id = fields.IntField(primary_key=True)
  name = fields.CharField(max_length=40)
  type_of_animal = fields.CharEnumField(AnimalType)
  subtype = fields.CharField(null=True, max_length=40)
  weight = fields.FloatField(null=True)
  birthday = fields.DateField()
  profile_picture_src = fields.CharField(null=True, max_length=120)
  owner_id = fields.ForeignKeyField("models.Owner", related_name="pets")
  posted_date = fields.DatetimeField(auto_now_add=True)
  last_updated = fields.DatetimeField(auto_now=True)
  profile_bio = fields.TextField(null=True)

class Availability(models.Model):
  id = fields.IntField(primary_key=True)
  appuser_id = fields.IntField()
  appuser_type = fields.CharEnumField(UserType)
  start_date = fields.DateField()
  end_date = fields.DateField()

class Review(models.Model):
  id = fields.IntField(primary_key=True)
  author_appuser_id = fields.ForeignKeyField("models.Appuser", related_name="author_reviews")
  recipient_appuser_type = fields.CharEnumField(UserType)
  comment = fields.TextField(null=True)
  score = fields.IntField(null=True)
  recipient_appuser_id = fields.ForeignKeyField("models.Appuser", related_name="recipient_reviews")
  submission_date = fields.DatetimeField(auto_now_add=True)

class Inquiry(models.Model):
  id = fields.IntField(primary_key=True)
  owner_appuser_id = fields.ForeignKeyField("models.Appuser", related_name="owner_inquiries")
  sitter_appuser_id = fields.ForeignKeyField("models.Appuser", related_name="sitter_inquiries")
  inquiry_status = fields.CharEnumField(InquiryStatus, default=InquiryStatus.REQUESTED)
  start_date = fields.DateField()
  end_date = fields.DateField()
  desired_service = fields.CharEnumField(PetServices)
  pet_id_list = fields.CharField(max_length=80)
  additional_info = fields.TextField(null=True)
  inquiry_submitted = fields.DatetimeField(auto_now_add=True)
  inquiry_finalized = fields.DatetimeField(null=True)

class Message(models.Model):
  id = fields.IntField(primary_key=True)
  inquiry_id = fields.ForeignKeyField("models.Inquiry", related_name="messages")
  author_appuser_id = fields.ForeignKeyField("models.Appuser", related_name="author_messages")
  recipient_appuser_id = fields.ForeignKeyField("models.Appuser", related_name="recipient_messages")
  content = fields.TextField()
  time_sent = fields.DatetimeField(auto_now_add=True)