# Mugi Backend

Live at https://mugi-backend.onrender.com
API documentation can be found at https://mugi-backend.onrender.com/docs

## Purpose

- To help pet owners find people to watch or check on their pets while they are away

## Technologies Used

- Python
- FastAPI
- Tortoise ORM
- PostgreSQL

## Setup

### Prerequisites:

- Python is installed
- Poetry is installed
- PostgreSQL is installed

### Initialization

Using `psql`, run `CREATE DATABASE petsitter;` to make the database

In terminal, run `poetry install` to install dependencies

In terminal, run `poetry run start` to start the server, create the database tables into `petsitter`, and have them seeded with sample data