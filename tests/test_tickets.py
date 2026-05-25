# Tests for: POST /tickets/, GET /tickets/, PUT /tickets/{id}/status, PUT /tickets/{id}/assign
# auth_headers  = logged in as a regular user
# admin_headers = logged in as an admin user


def test_create_ticket_success(client, auth_headers):
	# A logged-in user should be able to create a ticket
	# Response should contain the ticket details with default status "open"
	response = client.post("/tickets/", json={"title": "Bug report", "description": "Something broke"}, headers=auth_headers)
	assert response.status_code == 201
	data = response.json()
	assert data["title"] == "Bug report"
	assert data["status"] == "open"


def test_create_ticket_unauthorized(client):
	# Trying to create a ticket without logging in should be rejected with 401
	response = client.post("/tickets/", json={"title": "Bug", "description": "desc"})
	assert response.status_code == 401


def test_user_sees_only_own_tickets(client, auth_headers):
	# A regular user should only see tickets they created, not others'
	client.post("/tickets/", json={"title": "My ticket", "description": "desc"}, headers=auth_headers)
	response = client.get("/tickets/", headers=auth_headers)
	assert response.status_code == 200
	tickets = response.json()
	assert len(tickets) == 1
	assert tickets[0]["title"] == "My ticket"


def test_admin_sees_all_tickets(client, auth_headers, admin_headers):
	# Admin should see every ticket regardless of who created it
	client.post("/tickets/", json={"title": "User ticket", "description": "desc"}, headers=auth_headers)
	client.post("/tickets/", json={"title": "Admin ticket", "description": "desc"}, headers=admin_headers)
	response = client.get("/tickets/", headers=admin_headers)
	assert response.status_code == 200
	assert len(response.json()) == 2  # both tickets visible to admin


def test_update_status_as_admin(client, auth_headers, admin_headers):
	# Admin should be able to change a ticket's status
	ticket = client.post("/tickets/", json={"title": "t", "description": "d"}, headers=auth_headers).json()
	response = client.put(f"/tickets/{ticket['id']}/status", json={"status": "closed"}, headers=admin_headers)
	assert response.status_code == 200


def test_update_status_forbidden_for_user(client, auth_headers):
	# A regular user should NOT be able to change ticket status — only admins can
	ticket = client.post("/tickets/", json={"title": "t", "description": "d"}, headers=auth_headers).json()
	response = client.put(f"/tickets/{ticket['id']}/status", json={"status": "closed"}, headers=auth_headers)
	assert response.status_code == 403  # 403 Forbidden


def test_update_status_ticket_not_found(client, admin_headers):
	# Trying to update a ticket that doesn't exist should return 404
	response = client.put("/tickets/9999/status", json={"status": "closed"}, headers=admin_headers)
	assert response.status_code == 404


def test_assign_ticket_as_admin(client, auth_headers, admin_headers):
	# Admin should be able to assign a ticket to a user
	# We get the admin's id from /profile/ and assign the ticket to them
	ticket = client.post("/tickets/", json={"title": "t", "description": "d"}, headers=auth_headers).json()
	admin_profile = client.get("/profile/", headers=admin_headers).json()
	response = client.put(f"/tickets/{ticket['id']}/assign", json={"assigned_to": admin_profile["id"]}, headers=admin_headers)
	assert response.status_code == 200


def test_assign_ticket_forbidden_for_user(client, auth_headers):
	# A regular user should NOT be able to assign tickets — only admins can
	ticket = client.post("/tickets/", json={"title": "t", "description": "d"}, headers=auth_headers).json()
	response = client.put(f"/tickets/{ticket['id']}/assign", json={"assigned_to": 1}, headers=auth_headers)
	assert response.status_code == 403  # 403 Forbidden


def test_filter_tickets_by_status(client, auth_headers, admin_headers):
	# Create two tickets, close one of them, then filter by status=closed
	# Should return only the closed ticket
	client.post("/tickets/", json={"title": "open ticket", "description": "d"}, headers=auth_headers)
	ticket = client.post("/tickets/", json={"title": "closed ticket", "description": "d"}, headers=auth_headers).json()
	client.put(f"/tickets/{ticket['id']}/status", json={"status": "closed"}, headers=admin_headers)

	response = client.get("/tickets/?status=closed", headers=auth_headers)
	assert response.status_code == 200
	assert len(response.json()) == 1
	assert response.json()[0]["title"] == "closed ticket"


def test_search_tickets_by_title(client, auth_headers):
	# Create two tickets with different titles, then search for one by keyword
	# Should return only the matching ticket
	client.post("/tickets/", json={"title": "login bug", "description": "d"}, headers=auth_headers)
	client.post("/tickets/", json={"title": "payment issue", "description": "d"}, headers=auth_headers)

	response = client.get("/tickets/?search=login", headers=auth_headers)
	assert response.status_code == 200
	assert len(response.json()) == 1
	assert response.json()[0]["title"] == "login bug"
