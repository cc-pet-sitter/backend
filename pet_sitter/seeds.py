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
    content=f"Hey, how are you doing, {recipient.firstname}?"
  )
  print(f"Message sent from Appuser {initiator.id} for Appuser {recipient.id}")
  await models.Message.create(
    inquiry=inquiry,
    author_appuser=recipient,
    recipient_appuser=initiator,
    content=f"I'm doing great! How about you, {initiator.firstname}?"
  )
  print(f"Message sent from Appuser {recipient.id} for Appuser {initiator.id}")

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

  print(f"Appuser {author.id} left a {randomScore}-star review for Appuser {recipient.id}")

animal_breeds = {
    "dog": ["Labrador Retriever", "German Shepherd", "Golden Retriever"],
    "cat": ["Persian", "Maine Coon", "Siamese"],
    "fish": ["Goldfish", "Betta", "Guppy"],
    "bird": ["Parakeet", "Cockatiel", "African Grey Parrot"],
    "rabbit": ["Himalayan", "Mini Rex", "Holland Lop"]
}

top_pet_names = {
    "dog": ["Bella", "Max", "Luna", "Charlie", "Lucy", "Maru", "Hana", "Riku", "Kuro", "Chibi"],
    "cat": ["Milo", "Simba", "Oliver", "Lily", "Chloe", "Momo", "Sora", "Kiki", "Tora", "Yuki"],
    "fish": ["Nibbles", "Bubbles", "Finn", "Goldie", "Splash", "Koi", "Sui", "Maru", "Beni", "Sora"],
    "bird": ["Tweety", "Sunny", "Buddy", "Kiwi", "Sky", "Tori", "Hato", "Mimi", "Chiroru", "Sora"],
    "rabbit": ["Thumper", "Coco", "Flopsy", "Bunny", "Peanut", "Usagi", "Mochi", "Haru", "Purin", "Yume"]
}

pet_biographies = [
    "Always ready for a walk and loves cuddling after a long day of play.",
    "A curious explorer who loves to perch in the sun and watch the world go by.",
    "Loves to swim and chase after anything that moves in the water.",
    "Affectionate and mischievous, always getting into trouble with a wagging tail.",
    "A playful companion who enjoys snuggling up with a soft blanket at night.",
    "Quiet and gentle, yet always watching over the house with keen eyes.",
    "A foodie at heart who will always be first in line for dinner time.",
    "Adventurous and brave, with a heart full of energy for every new day.",
    "Enjoys a good nap as much as a fun game, always finding a sunny spot to rest.",
    "Loyal and protective, ready to keep an eye on the family no matter what."
]

async def create_pet(appuser: int):
  randomAnimal = fake.random_element(elements=["dog", "cat", "fish", "bird", "rabbit"])

  pet = await models.Pet.create(
    name=fake.random_element(elements=top_pet_names[randomAnimal]),
    type_of_animal=randomAnimal,
    subtype=fake.random_element(elements=animal_breeds[randomAnimal]),
    weight=randint(1,30),
    birthday=fake.date_time_this_decade(True, False),
    known_allergies="None",
    medications="None",
    special_needs="None",
    profile_picture_src=fake.random_element(elements=photos),
    pet_bio_picture_src_list=f'{fake.random_element(elements=photos)},{fake.random_element(elements=photos)},{fake.random_element(elements=photos)}',
    appuser=appuser,
    profile_bio=fake.random_element(elements=pet_biographies),
  )

  print(f"Added {pet.name} the {pet.type_of_animal} ({pet.subtype}) for Appuser {appuser.id}")

async def get_all_pets_for_user(appuser_id: int): 
  userPetsArray = await models.Pet.filter(appuser_id=appuser_id)

  if userPetsArray:
    return userPetsArray
  else:
    return []

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
        account_created=fake.date_time_this_year(True, False),
        last_updated=fake.date_time_this_year(True, False),
        last_login=fake.date_time_this_year(True, False),
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
      else:
         randomPetCount = randint(1,3)
         for i in range(randomPetCount):
          await create_pet(appuser)

  for i in range(100):  # Create fake inquiries
      owner = choice([user for user in appusers if not user.is_sitter])  # Ensure the owner is not a sitter
      sitter = choice([user for user in appusers if user.is_sitter])  # Ensure the sitter is a sitter
      
      start_date, end_date = generate_date_range()

      petList = await get_all_pets_for_user(owner.id)
      pet_id_list = ""

      for i in range(len(petList)):
        if not pet_id_list:
            pet_id_list += str(petList[i].id)
        else:
            pet_id_list += "," + str(petList[i].id)

      inquiry = await models.Inquiry.create(
          owner_appuser=owner,
          sitter_appuser=sitter,
          inquiry_status=choice([models.InquiryStatus.REQUESTED, models.InquiryStatus.APPROVED, models.InquiryStatus.REJECTED]),
          start_date=start_date,
          end_date=end_date,
          desired_service=choice([models.PetServices.OWNER_HOUSE, models.PetServices.SITTER_HOUSE, models.PetServices.VISIT]),
          pet_id_list=pet_id_list, 
          additional_info=fake.text(max_nb_chars=100),
          inquiry_submitted=fake.date_time_this_year(True, False),
          inquiry_finalized=fake.date_time_this_year(True, False) if choice([True, False]) else None
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