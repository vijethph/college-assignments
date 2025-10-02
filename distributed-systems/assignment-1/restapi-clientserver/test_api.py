import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from main import app, get_session, User


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def get_test_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = get_test_session
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"message": "The service is healthy"}


def test_create_user():
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "email": "john@example.com"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["age"] == 30
    assert data["email"] == "john@example.com"
    assert data["id"] is not None


def test_get_users_empty():
    response = client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_users():
    user_data = {"first_name": "Jane", "last_name": "Smith", "age": 25, "email": "jane@example.com"}
    client.post("/users/", json=user_data)

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["first_name"] == "Jane"


def test_get_user_by_id():
    user_data = {"first_name": "Bob", "last_name": "Johnson", "age": 35, "email": "bob@example.com"}
    create_response = client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Bob"
    assert data["id"] == user_id


def test_get_user_not_found():
    response = client.get("/users/999")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_update_user():
    user_data = {"first_name": "Alice", "last_name": "Wilson", "age": 28, "email": "alice@example.com"}
    create_response = client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]

    update_data = {"age": 29}
    response = client.patch(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["age"] == 29
    assert data["first_name"] == "Alice"


def test_update_user_not_found():
    update_data = {"age": 30}
    response = client.patch("/users/999", json=update_data)
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_delete_user():
    user_data = {"first_name": "Charlie", "last_name": "Brown", "age": 40, "email": "charlie@example.com"}
    create_response = client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True

    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404


def test_delete_user_not_found():
    response = client.delete("/users/999")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_create_user_invalid_data():
    user_data = {"first_name": "Test"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_pagination():
    for i in range(5):
        user_data = {"first_name": f"User{i}", "last_name": "Test", "email": f"user{i}@example.com"}
        client.post("/users/", json=user_data)

    response = client.get("/users/?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    response = client.get("/users/?offset=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2