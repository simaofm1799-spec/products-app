import jwt
import pytest
from fastapi.testclient import TestClient

from common.dummyjson import dummyjson
from common.security import create_token
from main import app

client = TestClient(app)  # without `with`: the lifespan (and the real DummyJSON client) is not started

USER_BODY = {"firstName": "Ana", "lastName": "Silva"}
PRODUCT_BODY = {"price": 10, "title": "Pen"}

# action -> (method, path, body) for users and for products
ACTIONS = {
    "create": [("POST", "/api/users", USER_BODY), ("POST", "/api/products", PRODUCT_BODY)],
    "delete": [("DELETE", "/api/users/1", None), ("DELETE", "/api/products/1", None)],
    "read": [("GET", "/api/users/1", None), ("GET", "/api/products/1", None)],
    "update_patch": [("PATCH", "/api/users/1", {"age": 30}), ("PATCH", "/api/products/1", {"stock": 3})],
    "update_put": [("PUT", "/api/users/1", {"age": 30}), ("PUT", "/api/products/1", {"stock": 3})],
}

# role -> actions it may do (the permission matrix)
ALLOWED = {
    "admin": {"create", "delete", "read", "update_patch", "update_put"},
    "moderator": {"read", "update_patch", "update_put"},
    "user": {"read"},
}


@pytest.fixture(autouse=True)
def fake_dummyjson(monkeypatch):
    async def fake_request(method, path, **kwargs):
        return {"id": 1, "products": [], "users": []}

    monkeypatch.setattr(dummyjson, "request", fake_request)


def auth(role):
    token = create_token({"id": 1, "role": role, "username": "tester"})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("role", sorted(ALLOWED))
@pytest.mark.parametrize("action", sorted(ACTIONS))
def test_permission_matrix(role, action):
    for method, path, body in ACTIONS[action]:
        response = client.request(method, path, json=body, headers=auth(role))
        if action in ALLOWED[role]:
            assert response.status_code in (200, 201, 204), (role, method, path, response.text)
        else:
            assert response.status_code == 403, (role, method, path)
            assert response.json()["code"] == "FORBIDDEN"


@pytest.mark.parametrize("role", sorted(ALLOWED))
def test_everybody_can_list(role):
    for path in ("/api/users", "/api/products", "/api/products/analytics"):
        assert client.get(path, headers=auth(role)).status_code == 200


def test_unknown_role_gets_nothing():
    response = client.post("/api/users", json=USER_BODY, headers=auth("superuser"))
    assert response.status_code == 403


def test_token_without_role_is_treated_as_user():
    token = create_token({"id": 1, "username": "tester"})  # no "role" in the user
    response = client.delete("/api/users/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_no_token_is_401_not_403():
    response = client.post("/api/users", json=USER_BODY)
    assert response.status_code == 401
    assert response.json()["code"] == "TOKEN_MISSING"


def test_forged_token_is_rejected():
    forged = jwt.encode({"role": "admin", "sub": "1", "username": "x"}, "wrong-secret", algorithm="HS256")
    response = client.delete("/api/users/1", headers={"Authorization": f"Bearer {forged}"})
    assert response.status_code == 401
    assert response.json()["code"] == "TOKEN_INVALID"


def test_role_sent_by_the_client_is_ignored():
    headers = {**auth("user"), "X-Role": "admin"}
    response = client.post("/api/users?role=admin", json={**USER_BODY, "role": "admin"}, headers=headers)
    assert response.status_code == 403
