def test_create_complete_list_and_patch_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False
    assert "created_at" in item and "updated_at" in item

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["description"] == "Updated"


def test_action_item_validation_and_bad_request(client):
    r = client.post("/action-items/", json={"description": "   "})
    assert r.status_code == 422

    r = client.patch("/action-items/1", json={})
    assert r.status_code == 422

    r = client.get("/action-items/", params={"sort": "-unknown"})
    assert r.status_code == 400


def test_action_items_pagination_and_sorting(client):
    for description in ["Charlie task", "Bravo task", "Alpha task"]:
        r = client.post("/action-items/", json={"description": description})
        assert r.status_code == 201, r.text

    r = client.get("/action-items/", params={"sort": "description", "limit": 2})
    assert r.status_code == 200
    first_page = r.json()
    assert [item["description"] for item in first_page] == ["Alpha task", "Bravo task"]

    r = client.get("/action-items/", params={"sort": "description", "skip": 2, "limit": 2})
    assert r.status_code == 200
    second_page = r.json()
    assert [item["description"] for item in second_page] == ["Charlie task"]

