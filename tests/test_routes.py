import json
import os
from unittest.mock import patch

import pytest

import storage


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_file = tmp_path / "inventory.json"
    monkeypatch.setattr(storage, "DATA_FILE", str(test_file))

    from app import app

    app.config["TESTING"] = True
    return app.test_client()


def test_list_empty(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_get_update_delete(client):
    create = client.post(
        "/inventory",
        data=json.dumps({"product_name": "Flour", "price": 2, "stock": 5}),
        content_type="application/json",
    )
    assert create.status_code == 201
    item = create.get_json()
    item_id = item["id"]

    get_one = client.get(f"/inventory/{item_id}")
    assert get_one.status_code == 200
    assert get_one.get_json()["product_name"] == "Flour"

    patch = client.patch(
        f"/inventory/{item_id}",
        data=json.dumps({"stock": 10}),
        content_type="application/json",
    )
    assert patch.status_code == 200
    assert patch.get_json()["stock"] == 10

    delete = client.delete(f"/inventory/{item_id}")
    assert delete.status_code == 200

    missing = client.get(f"/inventory/{item_id}")
    assert missing.status_code == 404


@patch("openfood.fetch_by_barcode")
def test_lookup_barcode(mock_fetch, client):
    mock_fetch.return_value = {
        "product_name": "Nutella",
        "barcode": "3017624010701",
        "brands": "Ferrero",
    }
    response = client.get("/lookup/barcode/3017624010701")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Nutella"