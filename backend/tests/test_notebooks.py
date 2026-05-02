def test_create_and_list_notebooks_with_pagination_and_sorting(client):
    for name in ["Work", "Ideas", "Archive"]:
        r = client.post("/notebooks/", json={"name": name})
        assert r.status_code == 201, r.text

    r = client.get("/notebooks/", params={"sort": "name", "limit": 2})
    assert r.status_code == 200
    first_page = r.json()
    assert [nb["name"] for nb in first_page] == ["Archive", "Ideas"]

    r = client.get("/notebooks/", params={"sort": "name", "skip": 2, "limit": 2})
    assert r.status_code == 200
    second_page = r.json()
    assert [nb["name"] for nb in second_page] == ["Work"]


def test_notebook_invalid_sort_field(client):
    r = client.get("/notebooks/", params={"sort": "-unknown"})
    assert r.status_code == 400
