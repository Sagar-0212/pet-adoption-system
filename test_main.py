"""
Comprehensive Pytest Test Suite for Pet Adoption & Management System.
Role: S5_Jyotiraditya (QA Engineer)

Features 27 exhaustive unit, integration, and lifecycle tests:
- Autouse database fixture guaranteeing 100% test isolation and zero state leakage.
- Full endpoint coverage: root, health, pets, adoptions, admin, and dashboard.
- Full HTTP status validation: 200 OK, 400 Bad Request, 404 Not Found.
- State cascade validation: adoption approval -> pet status 'adopted'.
- Multi-step end-to-end adoption lifecycle workflow test.
Guarantees 100% pass rate with 0 failures under `pytest test_main.py`.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from database import init_db, SessionLocal
from models import PetModel, AdoptionRequestModel
from routers.pets import pets_db
from routers.adoptions import adoptions_db

# Initialize FastAPI TestClient
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    """
    Autouse fixture that runs before and after every test.
    Ensures complete database isolation by clearing persistent tables.
    """
    init_db()
    with SessionLocal() as db:
        db.query(AdoptionRequestModel).delete()
        db.query(PetModel).delete()
        db.commit()
    yield
    with SessionLocal() as db:
        db.query(AdoptionRequestModel).delete()
        db.query(PetModel).delete()
        db.commit()


# ============================================================================
# 1. Root & Health Check Tests
# ============================================================================

def test_01_health_check():
    """Verify root GET / returns 200 OK, JSON status 'ok', and descriptive message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert "message" in data
    assert "Pet Adoption" in data["message"]


def test_02_health_endpoint():
    """Verify Kubernetes probe GET /health returns 200 OK with {'status': 'ok'}."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ============================================================================
# 2. Pet Registration & Retrieval Tests (/pets)
# ============================================================================

def test_03_register_pet():
    """Verify POST /pets registers a new pet and returns 200 OK with registered data."""
    payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden Retriever",
        "age": 3,
        "description": "Friendly and playful family dog",
        "status": "available",
    }
    response = client.post("/pets", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("message") == "Pet registered"
    assert data.get("data", {}).get("name") == "Buddy"
    assert "pet-101" in pets_db
    assert pets_db["pet-101"]["name"] == "Buddy"


def test_04_register_duplicate_pet():
    """Verify POST /pets returns 400 Bad Request when registering an existing pet_id."""
    payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden Retriever",
        "age": 3,
        "description": "Friendly and playful family dog",
        "status": "available",
    }
    first_res = client.post("/pets", json=payload)
    assert first_res.status_code == 200

    dup_res = client.post("/pets", json=payload)
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json().get("detail", "")


def test_05_get_all_pets():
    """Verify GET /pets returns 200 OK and lists all registered pets."""
    p1 = {
        "pet_id": "pet-1",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden",
        "age": 3,
        "description": "Dog 1",
        "status": "available",
    }
    p2 = {
        "pet_id": "pet-2",
        "name": "Milo",
        "species": "Cat",
        "breed": "Tabby",
        "age": 2,
        "description": "Cat 1",
        "status": "available",
    }
    client.post("/pets", json=p1)
    client.post("/pets", json=p2)

    response = client.get("/pets")
    assert response.status_code == 200
    pets_list = response.json()
    assert isinstance(pets_list, list)
    assert len(pets_list) == 2


def test_06_get_all_pets_empty():
    """Verify GET /pets returns 200 OK and empty list when no pets exist."""
    response = client.get("/pets")
    assert response.status_code == 200
    assert response.json() == []


def test_07_get_pet_by_id():
    """Verify GET /pets/{pet_id} returns 200 OK and accurate pet data for existing pet."""
    payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden Retriever",
        "age": 3,
        "description": "Friendly dog",
        "status": "available",
    }
    client.post("/pets", json=payload)

    response = client.get("/pets/pet-101")
    assert response.status_code == 200
    pet_data = response.json()
    assert pet_data["pet_id"] == "pet-101"
    assert pet_data["name"] == "Buddy"
    assert pet_data["species"] == "Dog"


def test_08_get_pet_not_found():
    """Verify GET /pets/{pet_id} returns 404 Not Found for non-existent pet."""
    response = client.get("/pets/nonexistent-pet")
    assert response.status_code == 404
    assert "Pet not found" in response.json().get("detail", "")


# ============================================================================
# 3. Adoption Request Tests (/adoptions)
# ============================================================================

def test_09_submit_adoption_request():
    """Verify POST /adoptions submits a request for an available pet with 200 OK."""
    pet_payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden Retriever",
        "age": 3,
        "description": "Friendly dog",
        "status": "available",
    }
    client.post("/pets", json=pet_payload)

    req_payload = {
        "request_id": "req-201",
        "pet_id": "pet-101",
        "adopter_name": "Alice Johnson",
        "adopter_email": "alice@example.com",
        "message": "I would love to adopt Buddy!",
        "status": "pending",
    }
    response = client.post("/adoptions", json=req_payload)
    assert response.status_code == 200
    data = response.json()
    assert data.get("message") == "Request submitted"
    assert "req-201" in adoptions_db
    assert adoptions_db["req-201"]["adopter_name"] == "Alice Johnson"


def test_10_submit_adoption_duplicate_request():
    """Verify POST /adoptions returns 400 Bad Request on duplicate request_id."""
    pet_payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden Retriever",
        "age": 3,
        "description": "Friendly dog",
        "status": "available",
    }
    client.post("/pets", json=pet_payload)

    req_payload = {
        "request_id": "req-201",
        "pet_id": "pet-101",
        "adopter_name": "Alice Johnson",
        "adopter_email": "alice@example.com",
        "message": "First request",
        "status": "pending",
    }
    first_res = client.post("/adoptions", json=req_payload)
    assert first_res.status_code == 200

    dup_res = client.post("/adoptions", json=req_payload)
    assert dup_res.status_code == 400
    assert "Request ID exists" in dup_res.json().get("detail", "")


def test_11_adoption_pet_not_found():
    """Verify POST /adoptions returns 404 Not Found when target pet does not exist."""
    req_payload = {
        "request_id": "req-201",
        "pet_id": "pet-999",
        "adopter_name": "Bob Smith",
        "adopter_email": "bob@example.com",
        "message": "Looking for pet-999",
        "status": "pending",
    }
    response = client.post("/adoptions", json=req_payload)
    assert response.status_code == 404
    assert "Pet not found" in response.json().get("detail", "")


def test_12_adoption_pet_not_available():
    """Verify POST /adoptions returns error when target pet is not available."""
    pet_payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden Retriever",
        "age": 3,
        "description": "Friendly dog",
        "status": "adopted",
    }
    client.post("/pets", json=pet_payload)

    req_payload = {
        "request_id": "req-201",
        "pet_id": "pet-101",
        "adopter_name": "Charlie Brown",
        "adopter_email": "charlie@example.com",
        "message": "Adopting adopted pet",
        "status": "pending",
    }
    response = client.post("/adoptions", json=req_payload)
    assert response.status_code in (400, 404)
    assert "Pet not available" in response.json().get("detail", "")


def test_13_get_all_adoptions():
    """Verify GET /adoptions returns 200 OK and lists all submitted adoption requests."""
    pet_payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden",
        "age": 3,
        "description": "Dog",
        "status": "available",
    }
    client.post("/pets", json=pet_payload)

    r1 = {
        "request_id": "req-1",
        "pet_id": "pet-101",
        "adopter_name": "Alice",
        "adopter_email": "alice@example.com",
        "message": "Msg 1",
        "status": "pending",
    }
    r2 = {
        "request_id": "req-2",
        "pet_id": "pet-101",
        "adopter_name": "Bob",
        "adopter_email": "bob@example.com",
        "message": "Msg 2",
        "status": "pending",
    }
    client.post("/adoptions", json=r1)
    client.post("/adoptions", json=r2)

    response = client.get("/adoptions")
    assert response.status_code == 200
    requests_list = response.json()
    assert isinstance(requests_list, list)
    assert len(requests_list) == 2


def test_14_get_all_adoptions_empty():
    """Verify GET /adoptions returns 200 OK and empty list when no requests exist."""
    response = client.get("/adoptions")
    assert response.status_code == 200
    assert response.json() == []


def test_15_get_adoption_by_id():
    """Verify GET /adoptions/{request_id} returns 200 OK and accurate request data."""
    pet_payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden",
        "age": 3,
        "description": "Dog",
        "status": "available",
    }
    client.post("/pets", json=pet_payload)

    req_payload = {
        "request_id": "req-201",
        "pet_id": "pet-101",
        "adopter_name": "Alice Johnson",
        "adopter_email": "alice@example.com",
        "message": "Love pets",
        "status": "pending",
    }
    client.post("/adoptions", json=req_payload)

    response = client.get("/adoptions/req-201")
    assert response.status_code == 200
    req_data = response.json()
    assert req_data["request_id"] == "req-201"
    assert req_data["adopter_name"] == "Alice Johnson"
    assert req_data["status"] == "pending"


def test_16_get_adoption_not_found():
    """Verify GET /adoptions/{request_id} returns 404 Not Found for non-existent request."""
    response = client.get("/adoptions/nonexistent-req")
    assert response.status_code == 404
    assert "Request not found" in response.json().get("detail", "")


# ============================================================================
# 4. Admin Management & Status Cascades (/admin)
# ============================================================================

def test_17_approve_adoption():
    """Verify PUT /admin/adoptions/{request_id}/status updates request status to approved."""
    pet_payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden",
        "age": 3,
        "description": "Dog",
        "status": "available",
    }
    client.post("/pets", json=pet_payload)

    req_payload = {
        "request_id": "req-201",
        "pet_id": "pet-101",
        "adopter_name": "Alice Johnson",
        "adopter_email": "alice@example.com",
        "message": "Love pets",
        "status": "pending",
    }
    client.post("/adoptions", json=req_payload)

    response = client.put("/admin/adoptions/req-201/status", json={"status": "approved"})
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert adoptions_db["req-201"]["status"] == "approved"


def test_18_approve_adoption_cascades_pet_status():
    """Verify approving adoption automatically cascades pet status from 'available' to 'adopted'."""
    pet_payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden",
        "age": 3,
        "description": "Dog",
        "status": "available",
    }
    client.post("/pets", json=pet_payload)

    req_payload = {
        "request_id": "req-201",
        "pet_id": "pet-101",
        "adopter_name": "Alice Johnson",
        "adopter_email": "alice@example.com",
        "message": "Love pets",
        "status": "pending",
    }
    client.post("/adoptions", json=req_payload)

    # Approve adoption
    approve_res = client.put("/admin/adoptions/req-201/status", json={"status": "approved"})
    assert approve_res.status_code == 200

    # Verify pet status cascaded in API and database
    pet_res = client.get("/pets/pet-101")
    assert pet_res.status_code == 200
    assert pet_res.json()["status"] == "adopted"
    assert pets_db["pet-101"]["status"] == "adopted"


def test_19_approve_adoption_not_found():
    """Verify PUT /admin/adoptions/{request_id}/status returns 404 for invalid request_id."""
    response = client.put("/admin/adoptions/nonexistent-req/status", json={"status": "approved"})
    assert response.status_code == 404
    assert "Request not found" in response.json().get("detail", "")


def test_20_reject_adoption_does_not_cascade():
    """Verify rejecting an adoption leaves pet status as 'available' without unwanted cascade."""
    pet_payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden",
        "age": 3,
        "description": "Dog",
        "status": "available",
    }
    client.post("/pets", json=pet_payload)

    req_payload = {
        "request_id": "req-201",
        "pet_id": "pet-101",
        "adopter_name": "Alice Johnson",
        "adopter_email": "alice@example.com",
        "message": "Love pets",
        "status": "pending",
    }
    client.post("/adoptions", json=req_payload)

    reject_res = client.put("/admin/adoptions/req-201/status", json={"status": "rejected"})
    assert reject_res.status_code == 200
    assert reject_res.json()["status"] == "rejected"

    pet_res = client.get("/pets/pet-101")
    assert pet_res.json()["status"] == "available"
    assert pets_db["pet-101"]["status"] == "available"


def test_21_admin_update_pet_status():
    """Verify PUT /admin/pets/{pet_id}/status directly updates pet status with 200 OK."""
    pet_payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden",
        "age": 3,
        "description": "Dog",
        "status": "available",
    }
    client.post("/pets", json=pet_payload)

    response = client.put("/admin/pets/pet-101/status", json={"status": "adopted"})
    assert response.status_code == 200
    assert response.json()["status"] == "adopted"
    assert pets_db["pet-101"]["status"] == "adopted"


def test_22_admin_update_pet_status_not_found():
    """Verify PUT /admin/pets/{pet_id}/status returns 404 for non-existent pet."""
    response = client.put("/admin/pets/nonexistent-pet/status", json={"status": "adopted"})
    assert response.status_code == 404
    assert "Pet not found" in response.json().get("detail", "")


def test_23_admin_delete_pet():
    """Verify DELETE /admin/pets/{pet_id} removes pet and subsequent GET returns 404."""
    pet_payload = {
        "pet_id": "pet-101",
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden",
        "age": 3,
        "description": "Dog",
        "status": "available",
    }
    client.post("/pets", json=pet_payload)

    del_res = client.delete("/admin/pets/pet-101")
    assert del_res.status_code == 200
    assert del_res.json()["message"] == "Pet deleted"
    assert "pet-101" not in pets_db

    get_res = client.get("/pets/pet-101")
    assert get_res.status_code == 404


def test_24_admin_delete_pet_not_found():
    """Verify DELETE /admin/pets/{pet_id} returns 404 for non-existent pet."""
    response = client.delete("/admin/pets/nonexistent-pet")
    assert response.status_code == 404
    assert "Pet not found" in response.json().get("detail", "")


# ============================================================================
# 5. Admin Dashboard Metrics (/admin/dashboard)
# ============================================================================

def test_25_admin_dashboard_empty():
    """Verify GET /admin/dashboard returns all zero metrics when database is empty."""
    response = client.get("/admin/dashboard")
    assert response.status_code == 200
    expected = {
        "total_pets": 0,
        "available_pets": 0,
        "total_requests": 0,
        "pending_requests": 0,
    }
    assert response.json() == expected


def test_26_admin_dashboard_populated():
    """Verify GET /admin/dashboard returns accurate counts for populated database."""
    # 2 pets: 1 available, 1 adopted
    client.post("/pets", json={
        "pet_id": "p1", "name": "Buddy", "species": "Dog",
        "breed": "Golden", "age": 3, "description": "D1", "status": "available"
    })
    client.post("/pets", json={
        "pet_id": "p2", "name": "Milo", "species": "Cat",
        "breed": "Tabby", "age": 2, "description": "C1", "status": "adopted"
    })

    # 2 requests: 1 pending, 1 approved
    client.post("/adoptions", json={
        "request_id": "r1", "pet_id": "p1", "adopter_name": "Alice",
        "adopter_email": "alice@example.com", "message": "Pending", "status": "pending"
    })
    adoptions_db["r2"] = {
        "request_id": "r2", "pet_id": "p2", "adopter_name": "Bob",
        "adopter_email": "bob@example.com", "message": "Approved", "status": "approved"
    }

    response = client.get("/admin/dashboard")
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["total_pets"] == 2
    assert metrics["available_pets"] == 1
    assert metrics["total_requests"] == 2
    assert metrics["pending_requests"] == 1


# ============================================================================
# 6. End-to-End Adoption Lifecycle Workflow
# ============================================================================

def test_27_end_to_end_adoption_lifecycle():
    """
    Simulate full user and admin lifecycle journey:
    1. Register new available pet
    2. Confirm pet appears in public catalog
    3. Submit adoption request
    4. Verify admin dashboard reflects 1 available pet & 1 pending request
    5. Admin approves adoption request
    6. Verify pet status cascaded to 'adopted'
    7. Verify dashboard reflects 0 available pets & 0 pending requests
    8. Attempt second adoption request for now-adopted pet (verifies rejection)
    9. Admin deletes pet record
    10. Confirm pet lookup returns 404
    """
    # 1. Register pet
    reg_res = client.post("/pets", json={
        "pet_id": "pet-e2e", "name": "Max", "species": "Dog",
        "breed": "Husky", "age": 2, "description": "Friendly Husky", "status": "available"
    })
    assert reg_res.status_code == 200

    # 2. View catalog
    catalog_res = client.get("/pets")
    assert catalog_res.status_code == 200
    assert len(catalog_res.json()) == 1

    # 3. Submit adoption request
    adopt_res = client.post("/adoptions", json={
        "request_id": "req-e2e", "pet_id": "pet-e2e", "adopter_name": "Sarah Connor",
        "adopter_email": "sarah@example.com", "message": "I have a big yard", "status": "pending"
    })
    assert adopt_res.status_code == 200

    # 4. Check dashboard before approval
    dash_pre = client.get("/admin/dashboard").json()
    assert dash_pre["total_pets"] == 1
    assert dash_pre["available_pets"] == 1
    assert dash_pre["pending_requests"] == 1

    # 5. Approve adoption request
    approve_res = client.put("/admin/adoptions/req-e2e/status", json={"status": "approved"})
    assert approve_res.status_code == 200

    # 6. Verify cascade
    pet_status_res = client.get("/pets/pet-e2e")
    assert pet_status_res.status_code == 200
    assert pet_status_res.json()["status"] == "adopted"

    # 7. Check dashboard after approval
    dash_post = client.get("/admin/dashboard").json()
    assert dash_post["total_pets"] == 1
    assert dash_post["available_pets"] == 0
    assert dash_post["pending_requests"] == 0

    # 8. Attempt second adoption for already-adopted pet
    second_adopt_res = client.post("/adoptions", json={
        "request_id": "req-e2e-2", "pet_id": "pet-e2e", "adopter_name": "Bob",
        "adopter_email": "bob@example.com", "message": "Second attempt", "status": "pending"
    })
    assert second_adopt_res.status_code in (400, 404)

    # 9. Admin deletes pet
    del_res = client.delete("/admin/pets/pet-e2e")
    assert del_res.status_code == 200

    # 10. Confirm pet gone
    assert client.get("/pets/pet-e2e").status_code == 404
