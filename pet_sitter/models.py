from tortoise import fields, models
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

class Role(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)  # Maybe not for the MVP but having roles should be benefitial in the future e.g., 'owner', 'sitter', 'admin'

class Appuser(models.Model):
    id = fields.IntField(pk=True)
    firebase_uid = fields.CharField(max_length=128, unique=True)  # Firebase UID
    firstname = fields.CharField(null=True, max_length=40)
    lastname = fields.CharField(null=True, max_length=40)
    email = fields.CharField(unique=True, max_length=40)
    account_created = fields.DatetimeField(null=True, auto_now_add=True)
    last_updated = fields.DatetimeField(null=True, auto_now=True)
    last_login = fields.DatetimeField(null=True)
    profile_picture_src = fields.CharField(null=True, max_length=120)
    prefecture = fields.CharField(null=True, max_length=40)
    city_ward = fields.CharField(null=True, max_length=40)
    street_address = fields.CharField(null=True, max_length=40)
    postal_code = fields.CharField(null=True, max_length=40)
    account_language = fields.CharEnumField(AccountLanguage, default=AccountLanguage.ENGLISH, null=True)
    english_ok = fields.BooleanField(default=False, null=True)
    japanese_ok = fields.BooleanField(default=False, null=True)
    
    # Optional: Roles relationship
    roles: fields.ManyToManyRelation["Role"] = fields.ManyToManyField(
        "models.Role",
        related_name="users",
        through="user_roles",
    )

class Owner(models.Model):
    id = fields.IntField(primary_key=True)
    average_owner_rating = fields.FloatField(null=True)
    profile_bio = fields.TextField(null=True)
    bio_picture_src_list = fields.TextField(null=True)
    appuser = fields.OneToOneField("models.Appuser", related_name="owner_profile", on_delete=fields.CASCADE)

class Sitter(models.Model):
    id = fields.IntField(primary_key=True)
    average_sitter_rating = fields.FloatField(null=True)
    profile_bio = fields.TextField(null=True)
    bio_picture_src_list = fields.TextField(null=True)
    sitter_house_ok = fields.BooleanField(default=False, null=True)
    owner_house_ok = fields.BooleanField(default=False, null=True)
    visit_ok = fields.BooleanField(default=False, null=True)
    dogs_ok = fields.BooleanField(default=False, null=True)
    cats_ok = fields.BooleanField(default=False, null=True)
    fish_ok = fields.BooleanField(default=False, null=True)
    birds_ok = fields.BooleanField(default=False, null=True)
    rabbits_ok = fields.BooleanField(default=False, null=True)
    appuser = fields.OneToOneField("models.Appuser", related_name="sitter_profile", on_delete=fields.CASCADE)

class Pet(models.Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=40)
    type_of_animal = fields.CharEnumField(AnimalType)
    subtype = fields.CharField(null=True, max_length=40)
    weight = fields.FloatField(null=True)
    birthday = fields.DateField()
    known_allergies = fields.CharField(null=True, max_length=80)
    medications = fields.CharField(null=True, max_length=80)
    special_needs = fields.TextField(null=True)
    profile_picture_src = fields.CharField(null=True, max_length=120)
    owner = fields.ForeignKeyField("models.Owner", related_name="pets")
    posted_date = fields.DatetimeField(auto_now_add=True, null=True)
    last_updated = fields.DatetimeField(auto_now=True, null=True)
    profile_bio = fields.TextField(null=True)

class Availability(models.Model):
    id = fields.IntField(primary_key=True)
    appuser_id = fields.IntField()
    appuser_type = fields.CharEnumField(UserType)
    start_date = fields.DateField()
    end_date = fields.DateField()

class Review(models.Model):
    id = fields.IntField(primary_key=True)
    author_appuser = fields.ForeignKeyField("models.Appuser", related_name="author_reviews")
    recipient_appuser_type = fields.CharEnumField(UserType)
    comment = fields.TextField(null=True)
    score = fields.IntField()
    recipient_appuser = fields.ForeignKeyField("models.Appuser", related_name="recipient_reviews")
    submission_date = fields.DatetimeField(auto_now_add=True, null=True)

class Inquiry(models.Model):
    id = fields.IntField(primary_key=True)
    owner_appuser = fields.ForeignKeyField("models.Appuser", related_name="owner_inquiries")
    sitter_appuser = fields.ForeignKeyField("models.Appuser", related_name="sitter_inquiries")
    inquiry_status = fields.CharEnumField(InquiryStatus, default=InquiryStatus.REQUESTED)
    start_date = fields.DateField()
    end_date = fields.DateField()
    desired_service = fields.CharEnumField(PetServices)
    pet_id_list = fields.CharField(max_length=80, null=True)
    additional_info = fields.TextField(null=True)
    inquiry_submitted = fields.DatetimeField(auto_now_add=True, null=True)
    inquiry_finalized = fields.DatetimeField(null=True)

class Message(models.Model):
    id = fields.IntField(primary_key=True)
    inquiry = fields.ForeignKeyField("models.Inquiry", related_name="messages")
    author_appuser = fields.ForeignKeyField("models.Appuser", related_name="author_messages")
    recipient_appuser = fields.ForeignKeyField("models.Appuser", related_name="recipient_messages")
    content = fields.TextField()
    time_sent = fields.DatetimeField(auto_now_add=True, null=True)