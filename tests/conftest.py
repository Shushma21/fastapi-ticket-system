import os

# Set these BEFORE importing the app so the app uses SQLite instead of Postgres
# This ensures tests never touch your real database
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base
from app.auth import get_db
from app import models

SQLITE_URL = "sqlite:///./test.db"

# Create a separate test engine using SQLite (lightweight, no setup needed)
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
	# This replaces the real get_db() during tests
	# So every DB call in the app uses the test SQLite database instead of Postgres
	db = TestingSessionLocal()
	try:
		yield db
	finally:
		db.close()


# Tell FastAPI to use our test database instead of the real one
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
	# Create all tables in the test database before the test runs
	Base.metadata.create_all(bind=engine)

	# TestClient lets us make HTTP requests to the app without running a real server
	with TestClient(app) as c:
		yield c  # the test runs here

	# Drop all tables after the test — next test gets a clean empty database
	Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_headers(client):
	# Register a regular user
	client.post("/register/", json={
		"username": "testuser",
		"email": "testuser@example.com",
		"password": "testpass123"
	})

	# Log in to get a token
	response = client.post("/login/", data={
		"username": "testuser",
		"password": "testpass123"
	})

	token = response.json()["access_token"]

	# Return the Authorization header — any test that uses auth_headers
	# will automatically be logged in as this user
	return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_headers(client):
	# Register a user (there's no register-as-admin endpoint, so we register normally first)
	client.post("/register/", json={
		"username": "adminuser",
		"email": "adminuser@example.com",
		"password": "adminpass123"
	})

	# Directly update the role to "admin" in the test database
	db = TestingSessionLocal()
	user = db.query(models.User).filter(models.User.username == "adminuser").first()
	user.role = "admin"
	db.commit()
	db.close()

	# Log in as admin to get a token
	response = client.post("/login/", data={
		"username": "adminuser",
		"password": "adminpass123"
	})

	token = response.json()["access_token"]

	# Return the Authorization header for admin requests
	return {"Authorization": f"Bearer {token}"}
