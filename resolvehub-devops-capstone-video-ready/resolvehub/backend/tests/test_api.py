def sample_ticket(title="VPN access issue", **overrides):
    data = {"title": title, "description": "Unable to connect to company VPN", "requester": "Alex Morgan", "category": "IT Support", "priority": "High", "status": "Open"}
    data.update(overrides)
    return data

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200 and response.json()["status"] == "healthy"

def test_readiness(client):
    response = client.get("/ready")
    assert response.status_code == 200

def test_create_ticket(client):
    response = client.post("/api/tickets", json=sample_ticket())
    assert response.status_code == 201
    assert response.json()["title"] == "VPN access issue"
    assert response.json()["id"] > 0

def test_list_and_filter_tickets(client):
    client.post("/api/tickets", json=sample_ticket())
    client.post("/api/tickets", json=sample_ticket("Laptop request", priority="Low"))
    response = client.get("/api/tickets", params={"priority": "High"})
    assert response.status_code == 200 and len(response.json()) == 1

def test_get_ticket_not_found(client):
    assert client.get("/api/tickets/999").status_code == 404

def test_update_ticket(client):
    ticket = client.post("/api/tickets", json=sample_ticket()).json()
    response = client.put(f"/api/tickets/{ticket['id']}", json={"status": "In Progress"})
    assert response.status_code == 200 and response.json()["status"] == "In Progress"

def test_delete_ticket(client):
    ticket = client.post("/api/tickets", json=sample_ticket()).json()
    assert client.delete(f"/api/tickets/{ticket['id']}").status_code == 204
    assert client.get(f"/api/tickets/{ticket['id']}").status_code == 404

def test_stats(client):
    client.post("/api/tickets", json=sample_ticket())
    response = client.get("/api/tickets/stats")
    assert response.status_code == 200 and response.json()["total"] == 1

def test_validation_rejects_short_title(client):
    assert client.post("/api/tickets", json=sample_ticket("x")).status_code == 422
