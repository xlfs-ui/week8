def test_create_list_and_patch_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    assert "created_at" in data and "updated_at" in data

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/", params={"q": "Hello", "limit": 10, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    note_id = data["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["title"] == "Updated"


def test_delete_note(client):
    r = client.post("/notes/", json={"title": "Delete me", "content": "temp"})
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_note_validation_and_bad_request(client):
    r = client.post("/notes/", json={"title": "   ", "content": "ok"})
    assert r.status_code == 422

    r = client.patch("/notes/1", json={})
    assert r.status_code == 422

    r = client.get("/notes/", params={"sort": "-unknown"})
    assert r.status_code == 400


def test_notes_pagination_and_sorting(client):
    for title in ["Charlie", "Bravo", "Alpha"]:
        r = client.post("/notes/", json={"title": title, "content": f"{title} body"})
        assert r.status_code == 201, r.text

    r = client.get("/notes/", params={"sort": "title", "limit": 2})
    assert r.status_code == 200
    first_page = r.json()
    assert [n["title"] for n in first_page] == ["Alpha", "Bravo"]

    r = client.get("/notes/", params={"sort": "title", "skip": 2, "limit": 2})
    assert r.status_code == 200
    second_page = r.json()
    assert [n["title"] for n in second_page] == ["Charlie"]

