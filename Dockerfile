FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
COPY pet_sitter ./pet_sitter

RUN poetry install

EXPOSE 8000

CMD ["poetry", "run", "start"]

