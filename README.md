# FastAPI Ticket Management System

A backend REST API built with FastAPI for managing support tickets, featuring OAuth2 + JWT authentication and role-based authorization.

## Features
- User registration & login with OAuth2 + JWT authentication
- Role-based authorization (Admin / Agent / User)
- Full CRUD API for tickets
- PostgreSQL database with SQLAlchemy ORM
- Alembic migrations
- Dockerized for easy deployment
- Automated test suite with pytest + conftest fixtures

## Tech Stack
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Alembic (migrations)
- Docker / docker-compose
- pytest

## Setup
\`\`\`
git clone https://github.com/Shushma21/fastapi-ticket-system
cd fastapi-ticket-system
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
\`\`\`

## Running with Docker
\`\`\`
docker-compose up --build
\`\`\`

## Running Tests
\`\`\`
pytest
\`\`\`

## API Docs
Visit \`http://127.0.0.1:8000/docs\` for interactive Swagger documentation.
