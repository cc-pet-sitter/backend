# Mugi Backend

- Live on Render at [backend.mugi.pet](https://backend.mugi.pet)
- API documentation can be found at [backend.mugi.pet/docs](https://backend.mugi.pet/docs)
- Database schema can be found at [dbdiagram.io/d/pet-sitter-673b448ee9daa85acad632f0](https://dbdiagram.io/d/pet-sitter-673b448ee9daa85acad632f0)

## About the Frontend

- Live on Render at [mugi.pet](https://mugi.pet)
- Its repo is located at https://github.com/cc-pet-sitter/frontend

## Purpose of App

- To help pet owners find people to watch or check on their pets while they are away

## Technologies Used

- Python
- FastAPI
- Tortoise ORM
- PostgreSQL
- Firebase

## Setup

### Prerequisites:

- Python is installed
- Poetry is installed
- PostgreSQL is installed
- This repo has been cloned locally

### Initial Configuration

1. Using `psql`, run `CREATE DATABASE petsitter;` to make the database

2. Create a `.env` file in root directory of your local copy of this repo

3. In your `.env` file, add the following three variables and assign their values as follows:
  - `DATABASE_URL`: Value should be the path specific to your local database (starting with `postgres://`)
  
  - `FIREBASE_CREDENTIALS`: Value should be the entire firebase-adminsdk `.json` credential file encoded in base64, as received from an existing team member
  
  - `FRONTEND_BASE_URL`: Value should be `http://localhost:5173`

### Application Startup

1. In terminal, run `poetry install` to install dependencies

2. In terminal, run `poetry run start` to start the server, create the database tables into `petsitter`, and have them seeded with sample data

3. The application is ready for use when see the ouput `INFO: Application startup complete.` in your terminal
