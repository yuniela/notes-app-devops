def test_register(client):
    res = client.post("/api/register", json={
        "user_name": "testuser",
        "password": "1234"
    })
    assert res.status_code == 201
    assert "user_name" in res.get_json()
