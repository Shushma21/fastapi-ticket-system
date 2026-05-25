# Tests for: POST /register/, POST /login/, GET /profile/
# The `client` parameter gives us an HTTP client with a fresh empty database
# The `auth_headers` parameter gives us a logged-in user's token header


def test_register_success(client):
	# Should create a new user and return a user_id
	response = client.post("/register/", json={
		"username": "newuser",
		"email": "newuser@example.com",
		"password": "pass123"
	})
	assert response.status_code == 200
	assert "user_id" in response.json()


def test_register_duplicate_email(client):
	# Register once with an email, then try again with the same email
	# Second request should be rejected with 400
	client.post("/register/", json={"username": "user1", "email": "same@example.com", "password": "pass123"})
	response = client.post("/register/", json={"username": "user2", "email": "same@example.com", "password": "pass123"})
	assert response.status_code == 400
	assert response.json()["detail"] == "Email already exists"


def test_register_duplicate_username(client):
	# Same idea but with duplicate username
	client.post("/register/", json={"username": "samename", "email": "a@example.com", "password": "pass123"})
	response = client.post("/register/", json={"username": "samename", "email": "b@example.com", "password": "pass123"})
	assert response.status_code == 400
	assert response.json()["detail"] == "Username already exists"


def test_login_success(client):
	# Register a user, then log in — should return an access token
	client.post("/register/", json={"username": "testuser", "email": "test@example.com", "password": "pass123"})
	response = client.post("/login/", data={"username": "testuser", "password": "pass123"})
	assert response.status_code == 200
	data = response.json()
	assert "access_token" in data
	assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
	# Correct username but wrong password — should return 401 Unauthorized
	client.post("/register/", json={"username": "testuser", "email": "test@example.com", "password": "pass123"})
	response = client.post("/login/", data={"username": "testuser", "password": "wrongpass"})
	assert response.status_code == 401


def test_login_user_not_found(client):
	# Username doesn't exist — should return 404 Not Found
	response = client.post("/login/", data={"username": "nobody", "password": "pass123"})
	assert response.status_code == 404


def test_profile_returns_user(client, auth_headers):
	# auth_headers already has a logged-in user (testuser)
	# Profile should return their details but NOT the password
	response = client.get("/profile/", headers=auth_headers)
	assert response.status_code == 200
	data = response.json()
	assert data["username"] == "testuser"
	assert data["email"] == "testuser@example.com"
	assert "password" not in data  # password must never be exposed in a response


def test_profile_unauthorized(client):
	# Calling /profile/ without a token should be rejected with 401
	response = client.get("/profile/")
	assert response.status_code == 401
