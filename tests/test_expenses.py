def novo_gasto(**extra):
    gasto = {
        "description": "Almoço",
        "amount": 35.5,
        "category": "Alimentação",
        "date": "2026-10-15",
    }
    gasto.update(extra)
    return gasto


def test_create_and_list(client, make_headers):
    headers = make_headers()
    created = client.post("/expenses", json=novo_gasto(), headers=headers)
    assert created.status_code == 201
    assert created.json()["description"] == "Almoço"

    listed = client.get("/expenses", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_invalid_amount(client, make_headers):
    headers = make_headers()
    response = client.post("/expenses", json=novo_gasto(amount=-10), headers=headers)
    assert response.status_code == 422


def test_update_and_delete(client, make_headers):
    headers = make_headers()
    gasto_id = client.post("/expenses", json=novo_gasto(), headers=headers).json()["id"]

    updated = client.patch(
        f"/expenses/{gasto_id}", json={"amount": 40.0}, headers=headers
    )
    assert updated.status_code == 200
    assert updated.json()["amount"] == 40.0
    assert updated.json()["description"] == "Almoço"  # não foi alterado

    deleted = client.delete(f"/expenses/{gasto_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.get(f"/expenses/{gasto_id}", headers=headers).status_code == 404


def test_user_cannot_access_other_users_expense(client, make_headers):
    ana = make_headers("ana")
    bruno = make_headers("bruno")
    gasto_id = client.post("/expenses", json=novo_gasto(), headers=ana).json()["id"]

    assert client.get(f"/expenses/{gasto_id}", headers=bruno).status_code == 404
    assert client.delete(f"/expenses/{gasto_id}", headers=bruno).status_code == 404
    assert client.get("/expenses", headers=bruno).json() == []


def test_filter_by_category_and_date(client, make_headers):
    headers = make_headers()
    client.post("/expenses", json=novo_gasto(), headers=headers)
    client.post(
        "/expenses",
        json=novo_gasto(category="Transporte", date="2026-09-01"),
        headers=headers,
    )

    by_category = client.get("/expenses?category=Transporte", headers=headers).json()
    assert len(by_category) == 1

    by_date = client.get("/expenses?start=2026-10-01", headers=headers).json()
    assert len(by_date) == 1
    assert by_date[0]["category"] == "Alimentação"


def test_summary(client, make_headers):
    headers = make_headers()
    client.post("/expenses", json=novo_gasto(amount=30), headers=headers)
    client.post("/expenses", json=novo_gasto(amount=20), headers=headers)
    client.post(
        "/expenses", json=novo_gasto(amount=50, category="Lazer"), headers=headers
    )

    response = client.get("/expenses/summary", headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "total": 100.0,
        "by_category": {"Alimentação": 50.0, "Lazer": 50.0},
    }
