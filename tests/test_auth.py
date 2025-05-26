def test_register(client):
    payload = {"user_name": "testuserregister", "password": "1234"}
    res = client.post("/api/register", json=payload)
    print("Response:", res.status_code, res.get_json())

    assert res.status_code == 201, f"Unexpected response: {res.get_json()}"


def test_login(client):
    #Register the user
    client.post("/api/register", json={
        "user_name": "testuserlogin",
        "password": "1234"
    })
    payload = {"user_name": "testuserlogin", "password": "1234"}
    res = client.post("/api/auth/login", json=payload)
    print("Response:", res.status_code, res.get_json())

    assert res.status_code == 200, f"Unexpected response: {res.get_json()}"
    assert "access_token" in res.get_json()


def test_create_note(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        'title': "My testing note",
        'content': "Some content for testing",
        "tags": "test"
    }

    res = client.post("/api/notes", json=payload, headers=headers)

    assert res.status_code == 201
    assert res.get_json()["title"] == "My testing note"


def test_get_notes(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}

    res = client.get("/api/notes", headers= headers)

    assert res.status_code == 200

def test_get_notes_returns_notes(client, auth_token, sample_notes):
    headers = {"Authorization": f"Bearer {auth_token}"}
    res = client.get("/api/notes", headers=headers)
    data = res.get_json()

    assert res.status_code == 200
    assert len(data) >= 3  # assuming sample_notes added at least 3
    assert any("DevOps" in note["title"] for note in data)
