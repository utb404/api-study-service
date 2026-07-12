"""Смоук-тесты основных сценариев песочницы."""
import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(
    tempfile.mkdtemp(), "test_academy.db"
)

import pytest
from fastapi.testclient import TestClient

from app.main import app

API_KEY = "sky-fire-9000"


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def token(client):
    resp = client.post("/auth/token", data={"username": "demo", "password": "demo1234"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_dragons_with_pagination(client):
    resp = client.get("/dragons", params={"limit": 2, "offset": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 6
    assert len(data["items"]) == 2


def test_filter_dragons_by_element(client):
    resp = client.get("/dragons", params={"element": "fire"})
    assert resp.status_code == 200
    assert all(d["element"] == "fire" for d in resp.json()["items"])


def test_dragon_not_found(client):
    resp = client.get("/dragons/99999")
    assert resp.status_code == 404


def test_register_and_login(client):
    resp = client.post(
        "/auth/register",
        json={"username": "tester", "email": "tester@academy.sky", "password": "secret123"},
    )
    assert resp.status_code == 201
    resp = client.post("/auth/token", data={"username": "tester", "password": "secret123"})
    assert resp.status_code == 200
    assert resp.json()["token_type"] == "bearer"


def test_register_duplicate_username(client):
    payload = {"username": "demo", "email": "other@academy.sky", "password": "secret123"}
    assert client.post("/auth/register", json=payload).status_code == 409


def test_me_requires_token(client, auth_headers):
    assert client.get("/auth/me").status_code == 401
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "demo"


def test_create_dragon_requires_auth(client):
    payload = {"name": "Безымянный", "element": "ice", "color": "белый"}
    assert client.post("/dragons", json=payload).status_code == 401


def test_dragon_crud_cycle(client, auth_headers):
    payload = {"name": "Тестозавр", "element": "storm", "color": "фиолетовый", "danger_level": 3}
    resp = client.post("/dragons", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    dragon_id = resp.json()["id"]

    resp = client.patch(
        f"/dragons/{dragon_id}", json={"tamed": True}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["tamed"] is True

    resp = client.put(
        f"/dragons/{dragon_id}",
        json={"name": "Тестозавр II", "element": "storm", "color": "синий"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Тестозавр II"

    assert client.delete(f"/dragons/{dragon_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/dragons/{dragon_id}").status_code == 404


def test_create_dragon_with_unknown_rider(client, auth_headers):
    payload = {"name": "Сирота", "element": "fire", "color": "рыжий", "rider_id": 99999}
    resp = client.post("/dragons", json=payload, headers=auth_headers)
    assert resp.status_code == 422


def test_rider_dragons(client):
    resp = client.get("/riders/1/dragons")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_delete_rider_with_dragons_conflict(client, auth_headers):
    resp = client.delete("/riders/1", headers=auth_headers)
    assert resp.status_code == 409


def test_quest_filters(client):
    resp = client.get("/quests", params={"status": "open", "min_difficulty": 9})
    assert resp.status_code == 200
    for quest in resp.json()["items"]:
        assert quest["status"] == "open"
        assert quest["difficulty"] >= 9


def test_delete_quest_requires_api_key(client, auth_headers):
    resp = client.post(
        "/quests",
        json={"title": "Одноразовый квест", "difficulty": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    quest_id = resp.json()["id"]

    assert client.delete(f"/quests/{quest_id}").status_code == 403
    assert (
        client.delete(f"/quests/{quest_id}", headers={"X-API-Key": "wrong"}).status_code == 403
    )
    assert (
        client.delete(f"/quests/{quest_id}", headers={"X-API-Key": API_KEY}).status_code == 204
    )


def test_sandbox_status(client):
    assert client.get("/sandbox/status/418").status_code == 418
    assert client.get("/sandbox/status/503").status_code == 503
    assert client.get("/sandbox/status/99").status_code == 400


def test_sandbox_echo(client):
    resp = client.post(
        "/sandbox/echo",
        params={"foo": "bar"},
        content=b'{"hello": "world"}',
        headers={"X-Custom": "test-value"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["method"] == "POST"
    assert data["query_params"] == {"foo": "bar"}
    assert data["headers"]["x-custom"] == "test-value"
    assert "hello" in data["body"]


def test_sandbox_random_names(client):
    resp = client.get("/sandbox/random-dragon-name", params={"count": 5})
    assert resp.status_code == 200
    assert len(resp.json()["names"]) == 5


def test_invalid_token_rejected(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert resp.status_code == 401
