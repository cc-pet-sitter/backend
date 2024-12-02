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
    "Loyal and protective, ready to keep an eye on the family no matter what.",
    "An explorer at heart, always sniffing out new places and making friends.",
    "A playful prankster, always making the family laugh with their antics.",
    "Loves chasing after balls and will never tire of a game of fetch.",
    "A gentle soul who enjoys being pampered with belly rubs and soft pets.",
    "Quiet and calm, often found lying peacefully next to their favorite human.",
    "Loves to curl up on the couch, content with a good chew toy and some peace.",
    "Adventurous spirit, always excited for a new trail to hike or path to walk.",
    "A sweet companion, always there to comfort and cuddle after a long day.",
    "Fearless and bold, always the first to explore new places and meet new people.",
    "A loyal friend, always there to keep you company no matter the time of day.",
    "A happy-go-lucky pet who brings joy to everyone they meet.",
    "Loves to learn new tricks, always eager to impress with their intelligence.",
    "A little bundle of energy, always bouncing around and spreading joy.",
    "A gentle and affectionate companion who loves to cuddle up on chilly nights.",
    "A social butterfly, always wanting to meet new pets and humans alike.",
    "A true adventurer, ready for any outdoor exploration or hike.",
    "Loves a good game of hide and seek, always finding the best hiding spots.",
    "A peaceful and calm pet, perfect for relaxing by your side after a long day.",
    "Always on the lookout for new adventures, never tired of discovering new places.",
    "Loyal to the core, always by your side, no matter where you go."
]

async def create_pet(appuser: int):
  randomAnimal = fake.random_element(elements=["dog", "cat", "fish", "bird", "rabbit"])

  pet = await models.Pet.create(
    name=fake.random_element(elements=top_pet_names[randomAnimal]),
    type_of_animal=randomAnimal,
    subtype=fake.random_element(elements=animal_breeds[randomAnimal]),
    gender=fake.random_element(elements=["male", "female"]),
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
  'Passionate animal lover, always excited to care for pets.',
  'Experienced expert in bird care and training with a deep understanding of their needs.',
  'Friendly and caring sitter, open to all pets, ensuring they feel at home.',
  'Professional pet sitter with a special love for dogs and years of experience.',
  'Enjoys providing attentive care for small pets, ensuring they stay happy and healthy.',
  'Experienced in handling cats and rabbits, offering personalized care for each.',
  'Caring and reliable sitter with years of experience looking after various pets.',
  'Specializing in exotic pets, providing expert care and attention to each unique animal.',
  'Skilled dog trainer and walker, dedicated to positive reinforcement techniques.',
  'Genuinely enjoys working with all kinds of pets, from dogs to small animals.',
  'Loves taking long walks and training dogs, building strong bonds along the way.',
  'Specializes in caring for exotic birds, providing the right environment and care.',
  'Open to providing care for any pet, with a focus on understanding their individual needs.',
  'Highly focused on dog care, ensuring they get all the attention and exercise they need.',
  'Loves working with small pets like rabbits, providing them with safe and nurturing care.',
  'Experienced with both cats and dogs, able to meet the needs of each pet with ease.',
  'Has expertise in training pets, ensuring they develop good habits and manners.',
  'Handles exotic pets with great care, understanding their specific needs and behaviors.',
  'Dog lover with excellent training skills, ensuring pets grow in a positive environment.',
  'Cat and rabbit expert, dedicated to offering the best care for these beloved pets.',
  'Passionate about creating a safe and comfortable environment for all pets.',
  'Experienced in caring for a variety of animals, from reptiles to furry friends.',
  'Loves interacting with pets of all kinds, ensuring they receive the best care possible.',
  'Committed to providing exceptional care and love for dogs, cats, and other pets.',
  'Enjoys bonding with pets through training and fun activities that stimulate both mind and body.',
  'A patient and dedicated sitter, always ensuring pets feel comfortable and loved.',
  'Professional pet care provider with a genuine affection for all animals.',
  'Skilled in handling exotic reptiles and birds, ensuring their well-being and health.',
  'A compassionate animal lover who enjoys the company of pets big and small.',
  'Focused on providing personalized care for each pet, making sure their needs are met.',
  'Enjoys providing enriching activities and companionship for pets, helping them thrive.',
  'Specializes in senior pet care, providing gentle support and attention for older animals.',
  'Caring for pets with love and patience, making them feel like part of the family.',
  'Has a keen interest in animal behavior and specializes in behavior modification for pets.',
  'Loves to care for pets during their recovery periods, offering comfort and care.',
  'Dedicated to providing quality exercise and mental stimulation for dogs.',
  'Experienced in looking after exotic mammals, offering individualized care for each species.',
  'Comfortable working with pets who require special needs or medical attention.',
  'Highly skilled in managing multi-pet households, ensuring harmony among pets.',
  'Provides pet care with a deep respect for the animal’s individual personality and needs.'
]

japan_prefectures = {
    "major": ["Saitama", "Chiba", "Tokyo", "Kanagawa"],
    "minor": ["Hokkaido", "Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima", 
    "Ibaraki", "Tochigi", "Gunma", "Niigata", "Toyama", "Ishikawa", "Fukui", "Yamanashi", "Nagano", "Gifu", 
    "Shizuoka", "Aichi", "Mie", "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara", "Wakayama", "Tottori", "Shimane", "Okayama", "Hiroshima", "Yamaguchi", "Tokushima", "Kagawa", "Ehime", "Kochi", "Fukuoka", "Saga", "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima", "Okinawa"]
}

japan_prefectures_cities = {
    "Hokkaido": ["Sapporo", "Hakodate", "Asahikawa", "Otaru"],
    "Aomori": ["Aomori", "Hachinohe"],
    "Iwate": ["Morioka", "Ichinoseki"],
    "Miyagi": ["Sendai", "Ishinomaki", "Shiogama"],
    "Akita": ["Akita", "Yokote"],
    "Yamagata": ["Yamagata", "Yonezawa"],
    "Fukushima": ["Fukushima", "Koriyama", "Aizuwakamatsu"],
    "Ibaraki": ["Mito", "Tsukuba", "Hitachi"],
    "Tochigi": ["Utsunomiya", "Ashikaga", "Nikko"],
    "Gunma": ["Maebashi", "Takasaki", "Isesaki"],
    "Saitama": ["Saitama", "Kawaguchi", "Koshigaya", "Omiya"],
    "Chiba": ["Chiba", "Narita", "Matsudo", "Kashiwa"],
    "Tokyo": ["Shinjuku", "Shibuya", "Ikebukuro", "Chiyoda"],
    "Kanagawa": ["Yokohama", "Kawasaki", "Sagamihara", "Odawara"],
    "Niigata": ["Niigata", "Joetsu", "Nagaoka"],
    "Toyama": ["Toyama", "Takaoka", "Uozu"],
    "Ishikawa": ["Kanazawa", "Wajima", "Tsubata"],
    "Fukui": ["Fukui", "Sakai"],
    "Yamanashi": ["Kofu", "Fujiyoshida", "Minami Alps"],
    "Nagano": ["Nagano", "Matsumoto", "Suwa"],
    "Gifu": ["Gifu", "Takayama", "Ogaki"],
    "Shizuoka": ["Shizuoka", "Hamamatsu", "Numazu"],
    "Aichi": ["Nagoya", "Toyota", "Okazaki", "Ichinomiya"],
    "Mie": ["Tsu", "Ise", "Yokkaichi"],
    "Shiga": ["Otsu", "Kusatsu", "Hikone"],
    "Kyoto": ["Kyoto", "Uji", "Kameoka"],
    "Osaka": ["Osaka", "Sakai", "Takaishi", "Hirakata"],
    "Hyogo": ["Kobe", "Himeji", "Amagasaki", "Takarazuka"],
    "Nara": ["Nara", "Yamatokoriyama"],
    "Wakayama": ["Wakayama", "Shingu"],
    "Tottori": ["Tottori", "Kurayoshi"],
    "Shimane": ["Matsue", "Izumo"],
    "Okayama": ["Okayama", "Kurashiki", "Tamano"],
    "Hiroshima": ["Hiroshima", "Kure", "Fukuyama"],
    "Yamaguchi": ["Yamaguchi", "Shimonoseki"],
    "Tokushima": ["Tokushima", "Anan"],
    "Kagawa": ["Takamatsu", "Marugame"],
    "Ehime": ["Matsuyama", "Imabari"],
    "Kochi": ["Kochi", "Nankoku"],
    "Fukuoka": ["Fukuoka", "Kitakyushu", "Kurume", "Nagasaki"],
    "Saga": ["Saga", "Karatsu"],
    "Nagasaki": ["Nagasaki", "Sasebo"],
    "Kumamoto": ["Kumamoto", "Yatsushiro", "Amakusa"],
    "Oita": ["Oita", "Beppu", "Nakatsu"],
    "Miyazaki": ["Miyazaki", "Nichinan"],
    "Kagoshima": ["Kagoshima", "Kanoya", "Izumi", "Satsumasendai"],
    "Okinawa": ["Naha", "Okinawa"]
}

async def seed_db():
  userAndInquiryCount = 400
  appusers = []

  for _ in range(userAndInquiryCount):
    prefectureCategory = fake.random_element(elements=["major", "minor"]) # uses major/minor to push more of the random results into Kanto
    prefecture = fake.random_element(elements=japan_prefectures[prefectureCategory])

    firstname = fake.first_name()
    lastname = fake.last_name()
    username = firstname.lower() + "." + lastname.lower() + str(randint(0,99))
    domain = "@" + fake.email().split("@")[1]
    email = username + domain

    appuser = await models.Appuser.create(
        firstname=firstname,
        lastname=lastname,
        email=email,
        firebase_user_id=fake.uuid4(),
        average_user_rating=randint(1,5),
        user_profile_bio=f'{fake.random_element(elements=bios)}',
        user_bio_picture_src_list=f'{fake.random_element(elements=photos)},{fake.random_element(elements=photos)},{fake.random_element(elements=photos)}',
        account_created=fake.date_time_this_year(True, False),
        last_updated=fake.date_time_this_year(True, False),
        last_login=fake.date_time_this_year(True, False),
        profile_picture_src=fake.random_element(elements=photos),
        prefecture=prefecture,
        city_ward=fake.random_element(elements=japan_prefectures_cities[prefecture]),
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
              sitter_profile_bio=f'{fake.random_element(elements=bios)}',
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

  for i in range(userAndInquiryCount):  # Create fake inquiries
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