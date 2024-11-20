#start server from root (backend) folder with "poetry run start"
from fastapi import FastAPI # type: ignore
import uvicorn # type: ignore
from tortoise import Tortoise # type: ignore
DATABASE_URL = "postgres://postgres:codechrysalis@localhost:5432/petsitter"

app = FastAPI()   

@app.get("/") 
async def main_route():     
  return "Hello world!"

# Register the models with Tortoise ORM
# register_tortoise(
#     app,
#     db_url=DATABASE_URL,
#     modules={"models": ["models"]},  # The path to your models
#     generate_schemas=True,  # Automatically generate the database schema
#     add_exception_handlers=True,  # Adds exception handlers for common ORM errors
# )

@app.on_event("startup")
async def startup():
    # Initialize Tortoise ORM with the database connection
    await Tortoise.init(db_url=DATABASE_URL, modules={"models": ["pet-sitter.models"]})
    await Tortoise.generate_schemas()

@app.on_event("shutdown")
async def shutdown():
    # Close the Tortoise connection when shutting down the app
    await Tortoise.close_connections()

def start():
    """Launched with poetry run start at root level"""
    uvicorn.run("pet-sitter.main:app", port=8000, host="0.0.0.0", reload=True)