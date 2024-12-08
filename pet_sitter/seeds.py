import pet_sitter.models as models
from faker import Faker # type: ignore
from enum import Enum
from random import choice, randint
from datetime import datetime, timedelta
import pet_sitter.locations as locations

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
    profile_picture_src=fake.random_element(elements=pets[randomAnimal]),
    pet_bio_picture_src_list=f'{fake.random_element(elements=yard)},{fake.random_element(elements=exterior)},{fake.random_element(elements=yard)}',
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

people = [
	"https://live.staticflickr.com/62/207176169_60738224b6_c.jpg",
	"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQmkRHRtkrvooPGjWA-GsLDUOyy8hV7F8fRQA&s",
	"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ7fEaFQ7CC3TK-PdJ6d0z5N_wTc1BQ-BLGVw&s",
	"https://2pawsupinc.com/wp-content/uploads/2018/05/why-hire-a-professional-pet-sitter.jpg",
	"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS7IWtIwnOwCcE2uGK82fdn303zm2foXLhxoA&s",
	"https://images.pexels.com/photos/29641277/pexels-photo-29641277/free-photo-of-man-embracing-labrador-retriever-outdoors.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/29583724/pexels-photo-29583724/free-photo-of-joyful-indian-girl-hugging-white-pomeranian.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/7210491/pexels-photo-7210491.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/9354547/pexels-photo-9354547.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/6530743/pexels-photo-6530743.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/5482207/pexels-photo-5482207.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/8489019/pexels-photo-8489019.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/5763553/pexels-photo-5763553.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/7481815/pexels-photo-7481815.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/12598764/pexels-photo-12598764.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/8359637/pexels-photo-8359637.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/17718338/pexels-photo-17718338/free-photo-of-man-and-woman-and-dog.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/10416690/pexels-photo-10416690.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/29632969/pexels-photo-29632969/free-photo-of-autumn-hiking-adventure-in-trondelag-norway.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
]

interior = [
	"https://images.pexels.com/photos/1080721/pexels-photo-1080721.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/1571460/pexels-photo-1571460.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/1743227/pexels-photo-1743227.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/2724748/pexels-photo-2724748.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/2227832/pexels-photo-2227832.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/2251247/pexels-photo-2251247.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/3797991/pexels-photo-3797991.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/2343468/pexels-photo-2343468.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/276724/pexels-photo-276724.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/3209045/pexels-photo-3209045.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/280232/pexels-photo-280232.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/280239/pexels-photo-280239.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
]

exterior = [
	"https://images.pexels.com/photos/280222/pexels-photo-280222.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/259588/pexels-photo-259588.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/209296/pexels-photo-209296.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/460695/pexels-photo-460695.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/210617/pexels-photo-210617.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/786944/pexels-photo-786944.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/2360673/pexels-photo-2360673.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
]

yard = [
	"https://images.pexels.com/photos/13975/pexels-photo-13975.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/7283/garden.jpg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/59321/pexels-photo-59321.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/198289/pexels-photo-198289.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
	"https://images.pexels.com/photos/1685164/pexels-photo-1685164.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
]

pets = {
  "dog" : [
    "https://cdn.sentidoanimal.es/wp-content/uploads/2024/05/cabecera_Dogsitter_pk.jpg",
    "https://d3544la1u8djza.cloudfront.net/APHI/Blog/2023/October/DogSitter-Hero.jpg",
    "https://images.pexels.com/photos/2607544/pexels-photo-2607544.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1805164/pexels-photo-1805164.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1851164/pexels-photo-1851164.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1458916/pexels-photo-1458916.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1619690/pexels-photo-1619690.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1198802/pexels-photo-1198802.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/160846/french-bulldog-summer-smile-joy-160846.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/5257587/pexels-photo-5257587.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1564506/pexels-photo-1564506.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/485294/pexels-photo-485294.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1629781/pexels-photo-1629781.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1954515/pexels-photo-1954515.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/3196887/pexels-photo-3196887.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
  ],
  "cat" : [
    "https://images.pexels.com/photos/45201/kitty-cat-kitten-pet-45201.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1643457/pexels-photo-1643457.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/2061057/pexels-photo-2061057.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/127028/pexels-photo-127028.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1183434/pexels-photo-1183434.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/923360/pexels-photo-923360.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1314550/pexels-photo-1314550.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1741205/pexels-photo-1741205.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/69932/tabby-cat-close-up-portrait-69932.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/257532/pexels-photo-257532.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1472999/pexels-photo-1472999.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/248280/pexels-photo-248280.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/982865/pexels-photo-982865.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
  ],
  "rabbit" : [
    "https://images.pexels.com/photos/2883510/pexels-photo-2883510.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/2061754/pexels-photo-2061754.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/6897439/pexels-photo-6897439.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/6897433/pexels-photo-6897433.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/4588065/pexels-photo-4588065.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/4588056/pexels-photo-4588056.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/3820509/pexels-photo-3820509.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/4588455/pexels-photo-4588455.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/4580783/pexels-photo-4580783.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/7121831/pexels-photo-7121831.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/6846044/pexels-photo-6846044.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/16042051/pexels-photo-16042051/free-photo-of-white-bunnies-in-a-wooden-hutch.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/7121825/pexels-photo-7121825.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
  ],
  "bird" : [
    "https://images.pexels.com/photos/46166/robin-european-robin-erithacus-rubecula-red-46166.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1526402/pexels-photo-1526402.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/5651223/pexels-photo-5651223.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1526410/pexels-photo-1526410.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/927500/pexels-photo-927500.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1774879/pexels-photo-1774879.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1040400/pexels-photo-1040400.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/29595854/pexels-photo-29595854/free-photo-of-vibrant-peach-faced-lovebird-on-hand.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/29595853/pexels-photo-29595853/free-photo-of-pastel-blue-lovebird-perched-on-hand.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/162140/duckling-birds-yellow-fluffy-162140.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1618424/pexels-photo-1618424.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/5103723/pexels-photo-5103723.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
  ],
  "fish" : [
    "https://images.pexels.com/photos/5966770/pexels-photo-5966770.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/7188173/pexels-photo-7188173.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1335971/pexels-photo-1335971.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/2156311/pexels-photo-2156311.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/3133396/pexels-photo-3133396.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/78790/perch-cichlid-discus-cichlid-freshwater-fish-78790.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/2156316/pexels-photo-2156316.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/128756/pexels-photo-128756.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1677116/pexels-photo-1677116.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/3905045/pexels-photo-3905045.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/1145274/pexels-photo-1145274.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "https://images.pexels.com/photos/12304385/pexels-photo-12304385.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
  ]
}

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

async def seed_db():
  userAndInquiryCount = 3000
  appusers = []

  for _ in range(userAndInquiryCount):
    prefectureCategory = fake.random_element(elements=["major", "minor"]) # uses major/minor to push more of the random results into Kanto
    prefecture = fake.random_element(elements=locations.japan_prefectures[prefectureCategory])

    firstname = fake.first_name()
    lastname = fake.last_name()
    username = firstname.lower() + "." + lastname.lower() + str(randint(0,9999))
    domain = "@" + fake.email().split("@")[1]
    email = username + domain

    appuser = await models.Appuser.create(
        firstname=firstname,
        lastname=lastname,
        email=email,
        firebase_user_id=fake.uuid4(),
        average_user_rating=randint(1,5),
        user_profile_bio=f'{fake.random_element(elements=bios)}',
        user_bio_picture_src_list=f'{fake.random_element(elements=interior)},{fake.random_element(elements=exterior)},{fake.random_element(elements=yard)}',
        account_created=fake.date_time_this_year(True, False),
        last_updated=fake.date_time_this_year(True, False),
        last_login=fake.date_time_this_year(True, False),
        profile_picture_src=fake.random_element(elements=people),
        prefecture=prefecture,
        city_ward=fake.random_element(elements=locations.japan_prefectures_cities[prefecture]),
        street_address=fake.street_address(),
        postal_code=fake_jp.zipcode(),  # Fake Japanese postal code
        account_language=fake.random_element(elements=["english", "japanese"]),
        english_ok=fake.boolean(),
        japanese_ok=fake.boolean(),
        is_sitter=True #fake.boolean() for random results
    )
    appusers.append(appuser)
    print(f"Created Appuser {_+1}: {appuser.firstname} {appuser.lastname} who lives in {appuser.prefecture} and speaks {appuser.account_language}")

  for appuser in appusers:
      if appuser.is_sitter:
          await models.Sitter.create(
              sitter_profile_bio=f'{fake.random_element(elements=bios)}',
              sitter_bio_picture_src_list=f'{fake.random_element(elements=interior)},{fake.random_element(elements=exterior)},{fake.random_element(elements=yard)}',
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
         
      randomPetCount = randint(1,3)
      for i in range(randomPetCount):
        await create_pet(appuser)

  for i in range(userAndInquiryCount):  # Create fake inquiries
      owner = choice([user for user in appusers])  # Owner can be any user since all appusers are owners by default
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