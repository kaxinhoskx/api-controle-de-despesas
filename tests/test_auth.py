def test_register_ok(client):
    response = client.post(
        "/auth/register", json={"username": "ana", "password": "senha123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "ana"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_duplicate_username(client):
    payload = {"username": "ana", "password": "senha123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409


def test_register_short_password(client):
    response = client.post("/auth/register", json={"username": "ana", "password": "123"})
    assert response.status_code == 422


def test_login_ok(client):
    client.post("/auth/register", json={"username": "ana", "password": "senha123"})
    response = client.post(
        "/auth/login", data={"username": "ana", "password": "senha123"}
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "ana", "password": "senha123"})
    response = client.post(
        "/auth/login", data={"username": "ana", "password": "errada123"}
    )
    assert response.status_code == 401


def test_expenses_require_token(client):
    assert client.get("/expenses").status_code == 401
    assert (
        client.get("/expenses", headers={"Authorization": "Bearer invalido"}).status_code
        == 401
    )
