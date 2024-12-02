import pet_sitter.models as models
from faker import Faker # type: ignore
from enum import Enum
from random import choice, randint
from datetime import datetime, timedelta

fake = Faker("en_US")  # English locale for names
fake_jp = Faker("ja_JP")  # Japanese locale for addresses

# Helper function to generate random date ranges
def generate_date_range():
    start_date = fake.date_time_this_year(before_now=True, after_now=False)
    end_date = fake.date_time_this_year(before_now=False, after_now=True)
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    return start_date, end_date

async def create_messages(inquiry: int, initiator: int, recipient: int):
  await models.Message.create(
    inquiry=inquiry,
    author_appuser=initiator,
    recipient_appuser=recipient,
    content="Hey, how are you doing?"
  )
  print(f"Message sent from Appuser {initiator} for Appuser {recipient}")
  await models.Message.create(
    inquiry=inquiry,
    author_appuser=recipient,
    recipient_appuser=initiator,
    content="I'm doing great! How about you?"
  )
  print(f"Message sent from Appuser {recipient} for Appuser {initiator}")

fakeOwnerCommentsList = [
   "Absolutely horrible. Never again.",
   "Not so great. Would not recommend.",
   "They were okay, but not like amazing. I wish they gave us more updates on our little baby.",
   "Good and reliable service. No real complaints.",
   "Fantastic service. I'll definitely be contacting them again."
]

fakeSitterCommentsList = [
   "Their pet is a monster and their house is a mess. Never again.",
   "They only mentioned the one pet in their request, but they actually had two that needed watching...",
   "It was a lot of work looking after all their pets. I might watch them again if they paid more.",
   "Their pet acts up sometimes, but is so cute. I'd watch them again.",
   "Their pet is so cute and well behaved. I'd watch them for free."
]

async def create_review(author: int, recipient: int, recipient_type: str):
  randomScore = randint(1,5)
  index = randomScore - 1

  await models.Review.create(
    author_appuser=author,
    recipient_appuser=recipient,
    recipient_appuser_type=recipient_type,
    score=randomScore,
    comment=fakeOwnerCommentsList[index] if recipient_type == "sitter" else fakeSitterCommentsList[index]
  )

  print(f"Appuser {author} left a {randomScore}-star review for Appuser {recipient}")

photos = [
   "https://live.staticflickr.com/62/207176169_60738224b6_c.jpg",
   "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmkRHRtkrvooPGjWA-GsLDUOyy8hV7F8fRQA&s",
   "https://d3544la1u8djza.cloudfront.net/APHI/Blog/2023/October/DogSitter-Hero.jpg",
   "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ7fEaFQ7CC3TK-PdJ6d0z5N_wTc1BQ-BLGVw&s",
   "https://cdn.sentidoanimal.es/wp-content/uploads/2024/05/cabecera_Dogsitter_pk.jpg",
   "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTW4r9cqwOBK4ObEJqQSj3BV2JYkwyZJCQhOw&s",
   "https://2pawsupinc.com/wp-content/uploads/2018/05/why-hire-a-professional-pet-sitter.jpg",
   "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS7IWtIwnOwCcE2uGK82fdn303zm2foXLhxoA&s",
   "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS7IWtIwnOwCcE2uGK82fdn303zm2foXLhxoA&s",
   "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTW4r9cqwOBK4ObEJqQSj3BV2JYkwyZJCQhOw&s"
]

bios = [
  'Animal lover based in Saitama.',
  'Expert in bird care and training.',
  'Friendly sitter, open to all pets.',
  'Professional sitter, loves dogs.',
  'Enjoys taking care of small pets.',
  'Experienced with cats and rabbits.',
  'Caring sitter with years of experience.',
  'Pet sitter specialising in exotic pets.',
  'Dog trainer and walker in Tokyo.',
  'Enjoys working with all kinds of pets.',
  'Loves walking and training dogs.',
  'Specialises in exotic birds.',
  'Open to caring for all pets.',
  'Focused on dog care.',
  'Loves working with small pets like rabbits.',
  'Experienced with both cats and dogs.',
  'Expertise in training pets.',
  'Handles exotic pets with care.',
  'Dog lover with training skills.',
  'Cat and rabbit expert.'
]

cities = {
   "Tokyo": ["Shibuya", "Shinjuku", "Minato", "Shinagawa"],
   "Chiba": ["Urayasu", "Funabashi", "Matsudo", "Narita"],
   "Kanagawa": ["Yokohama", "Kawasaki", "Kamakura", "Yokosuka"],
   "Saitama": ["Omiya", "Kawaguchi", "Koshigaya", "Kasukabe"]
}

async def seed_db():
  appusers = []

  for _ in range(100):
    prefecture = fake.random_element(elements=["Tokyo","Chiba","Saitama","Kanagawa"])

    appuser = await models.Appuser.create(
        firstname=fake.first_name(),
        lastname=fake.last_name(),
        email=fake.email(),
        firebase_user_id=fake.uuid4(),
        average_user_rating=randint(1,5),
        user_profile_bio=f'{fake.random_element(elements=bios)} {fake.random_element(elements=bios)} {fake.random_element(elements=bios)}',
        user_bio_picture_src_list=f'{fake.random_element(elements=photos)},{fake.random_element(elements=photos)},{fake.random_element(elements=photos)}',
        account_created=fake.date_time_this_year(),
        last_updated=fake.date_time_this_year(),
        last_login=fake.date_time_this_year(),
        profile_picture_src=fake.random_element(elements=photos),
        prefecture=prefecture,
        city_ward=fake.random_element(elements=cities[prefecture]),
        street_address=fake.street_address(),
        postal_code=fake_jp.zipcode(),  # Fake Japanese postal code
        account_language=fake.random_element(elements=["english", "japanese"]),
        english_ok=fake.boolean(),
        japanese_ok=fake.boolean(),
        is_sitter=fake.boolean()
    )
    appusers.append(appuser)
    print(f"Created Appuser {_+1}: {appuser.firstname} {appuser.lastname} who lives in {appuser.prefecture} and speaks {appuser.account_language}")

  for appuser in appusers:
      if appuser.is_sitter:
          await models.Sitter.create(
              sitter_profile_bio=f'{fake.random_element(elements=bios)} {fake.random_element(elements=bios)} {fake.random_element(elements=bios)}',
              sitter_bio_picture_src_list=f'{fake.random_element(elements=photos)},{fake.random_element(elements=photos)},{fake.random_element(elements=photos)}',
              sitter_house_ok=fake.boolean(),
              owner_house_ok=fake.boolean(),
              visit_ok=fake.boolean(),
              dogs_ok=fake.boolean(),
              cats_ok=fake.boolean(),
              fish_ok=fake.boolean(),
              birds_ok=fake.boolean(),
              rabbits_ok=fake.boolean(),
              appuser=appuser
          )
          print(f"Created a Sitter profile for Appuser {appuser.id}: {appuser.firstname} {appuser.lastname}")

          for _ in range(5):
            available_date = fake.date_time_this_year(False, True) # before_now: bool, after_now: bool
            await models.Availability.create(
              appuser=appuser,
              available_date=available_date
            )
            print(f"Sitter {appuser.firstname} is available on {available_date}")

  for i in range(100):  # Create fake inquiries
      owner = choice([user for user in appusers if not user.is_sitter])  # Ensure the owner is not a sitter
      sitter = choice([user for user in appusers if user.is_sitter])  # Ensure the sitter is a sitter
      
      start_date, end_date = generate_date_range()

      # Generate a list of pet IDs for the inquiry
      pet_id_list = "1,2,3,4,5" # This is hardcoded and fake for now because pets don't exist in the db yet

      inquiry = await models.Inquiry.create(
          owner_appuser=owner,
          sitter_appuser=sitter,
          inquiry_status=choice([models.InquiryStatus.REQUESTED, models.InquiryStatus.APPROVED, models.InquiryStatus.REJECTED]),
          start_date=start_date,
          end_date=end_date,
          desired_service=choice([models.PetServices.OWNER_HOUSE, models.PetServices.SITTER_HOUSE, models.PetServices.VISIT]),
          pet_id_list=pet_id_list, 
          additional_info=fake.text(max_nb_chars=100),
          inquiry_submitted=fake.date_time_this_year(),
          inquiry_finalized=fake.date_time_this_year() if choice([True, False]) else None
      )
      print(f"Created Inquiry of Status {inquiry.inquiry_status} for Owner {owner.firstname} to Sitter {sitter.firstname} from {start_date} to {end_date}")

      if i % 2 == 0:
        await create_messages(inquiry, owner, sitter)
      else:
        await create_messages(inquiry, sitter, owner)

      if inquiry.inquiry_status in [models.InquiryStatus.APPROVED]:
        await create_review(owner, sitter, "sitter")
        await create_review(sitter, owner, "owner")

  print("Seeding completed!")