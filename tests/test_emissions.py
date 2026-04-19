"""
Integration tests for Emissions routes.

Coverage:
  POST   /api/emissions/         – create (authenticated + unauthenticated)
  GET    /api/emissions/         – list (own records only, empty list)
  PUT    /api/emissions/{id}     – update (success, not-found, invalid id)
  DELETE /api/emissions/{id}     – delete (success, not-found, invalid id)
  GET    /api/emissions/stats    – aggregated stats per category
"""

import pytest
from fastapi.testclient import TestClient


# ── Sample payloads ───────────────────────────────────────────────────────────

_EMISSION_PAYLOAD = {
    "category": "Transport",
    "sub_category": "Petrol Car",
    "value": 12.5,
    "unit": "kg CO2e",
    "description": "Daily commute",
}

_INVALID_OBJECT_ID = "not-a-valid-objectid"


# ── /emissions (create) ───────────────────────────────────────────────────────

class TestCreateEmission:
    def test_create_emission_authenticated(self, client: TestClient, auth: dict):
        res = client.post("/api/emissions/", json=_EMISSION_PAYLOAD, headers=auth["headers"])
        assert res.status_code == 200
        body = res.json()
        assert body["category"] == "Transport"
        assert body["value"] == 12.5
        # Must include server-generated fields
        assert "_id" in body
        assert "user_id" in body
        assert "created_at" in body

    def test_create_emission_unauthenticated(self, client: TestClient):
        res = client.post("/api/emissions/", json=_EMISSION_PAYLOAD)
        assert res.status_code == 401

    def test_create_emission_missing_required_fields(self, client: TestClient, auth: dict):
        # category and value are required
        res = client.post("/api/emissions/", json={"unit": "kg CO2e"}, headers=auth["headers"])
        assert res.status_code == 422

    def test_create_emission_negative_value(self, client: TestClient, auth: dict):
        # Pydantic does not reject negative values by default; the record is
        # created and stored as-is (business rule enforcement, not schema)
        payload = {**_EMISSION_PAYLOAD, "value": -5.0}
        res = client.post("/api/emissions/", json=payload, headers=auth["headers"])
        assert res.status_code == 200


# ── /emissions (list) ─────────────────────────────────────────────────────────

class TestListEmissions:
    def test_list_emissions_empty(self, client: TestClient, auth: dict):
        res = client.get("/api/emissions/", headers=auth["headers"])
        assert res.status_code == 200
        assert res.json() == []

    def test_list_emissions_returns_own_records(self, client: TestClient, auth: dict):
        # Create two emissions for the authenticated user
        client.post("/api/emissions/", json=_EMISSION_PAYLOAD, headers=auth["headers"])
        client.post(
            "/api/emissions/",
            json={**_EMISSION_PAYLOAD, "category": "Food", "value": 7.2},
            headers=auth["headers"],
        )
        res = client.get("/api/emissions/", headers=auth["headers"])
        assert res.status_code == 200
        records = res.json()
        assert len(records) == 2

    def test_list_emissions_unauthenticated(self, client: TestClient):
        res = client.get("/api/emissions/")
        assert res.status_code == 401


# ── /emissions/{id} (update) ──────────────────────────────────────────────────

class TestUpdateEmission:
    def _create_one(self, client: TestClient, auth: dict) -> str:
        res = client.post("/api/emissions/", json=_EMISSION_PAYLOAD, headers=auth["headers"])
        return res.json()["_id"]

    def test_update_emission_success(self, client: TestClient, auth: dict):
        record_id = self._create_one(client, auth)
        update = {"value": 20.0, "description": "Updated commute"}
        res = client.put(f"/api/emissions/{record_id}", json=update, headers=auth["headers"])
        assert res.status_code == 200
        body = res.json()
        assert body["value"] == 20.0
        assert body["description"] == "Updated commute"

    def test_update_emission_not_found(self, client: TestClient, auth: dict):
        # Valid ObjectId format but non-existent document
        fake_id = "aaaaaaaaaaaaaaaaaaaaaaaa"
        res = client.put(f"/api/emissions/{fake_id}", json={"value": 1.0}, headers=auth["headers"])
        assert res.status_code == 404

    def test_update_emission_invalid_object_id(self, client: TestClient, auth: dict):
        res = client.put(
            f"/api/emissions/{_INVALID_OBJECT_ID}",
            json={"value": 1.0},
            headers=auth["headers"],
        )
        assert res.status_code == 404

    def test_update_emission_unauthenticated(self, client: TestClient, auth: dict):
        record_id = self._create_one(client, auth)
        res = client.put(f"/api/emissions/{record_id}", json={"value": 1.0})
        assert res.status_code == 401


# ── /emissions/{id} (delete) ──────────────────────────────────────────────────

class TestDeleteEmission:
    def _create_one(self, client: TestClient, auth: dict) -> str:
        res = client.post("/api/emissions/", json=_EMISSION_PAYLOAD, headers=auth["headers"])
        return res.json()["_id"]

    def test_delete_emission_success(self, client: TestClient, auth: dict):
        record_id = self._create_one(client, auth)
        res = client.delete(f"/api/emissions/{record_id}", headers=auth["headers"])
        assert res.status_code == 200
        assert "deleted" in res.json()["message"].lower()

    def test_delete_emission_not_found(self, client: TestClient, auth: dict):
        fake_id = "bbbbbbbbbbbbbbbbbbbbbbbb"
        res = client.delete(f"/api/emissions/{fake_id}", headers=auth["headers"])
        assert res.status_code == 404

    def test_delete_emission_invalid_object_id(self, client: TestClient, auth: dict):
        res = client.delete(f"/api/emissions/{_INVALID_OBJECT_ID}", headers=auth["headers"])
        assert res.status_code == 404

    def test_delete_emission_unauthenticated(self, client: TestClient, auth: dict):
        record_id = self._create_one(client, auth)
        res = client.delete(f"/api/emissions/{record_id}")
        assert res.status_code == 401

    def test_deleted_record_no_longer_listed(self, client: TestClient, auth: dict):
        record_id = self._create_one(client, auth)
        client.delete(f"/api/emissions/{record_id}", headers=auth["headers"])
        res = client.get("/api/emissions/", headers=auth["headers"])
        ids = [r["_id"] for r in res.json()]
        assert record_id not in ids


# ── /emissions/stats ──────────────────────────────────────────────────────────

class TestEmissionStats:
    def test_stats_empty(self, client: TestClient, auth: dict):
        res = client.get("/api/emissions/stats", headers=auth["headers"])
        assert res.status_code == 200
        assert res.json() == []

    def test_stats_aggregated_by_category(self, client: TestClient, auth: dict):
        # Create two Transport and one Food record
        for _ in range(2):
            client.post("/api/emissions/", json=_EMISSION_PAYLOAD, headers=auth["headers"])
        client.post(
            "/api/emissions/",
            json={**_EMISSION_PAYLOAD, "category": "Food", "value": 7.2},
            headers=auth["headers"],
        )
        res = client.get("/api/emissions/stats", headers=auth["headers"])
        assert res.status_code == 200
        stats = res.json()
        # Should have two groups: Transport and Food
        categories = {s["_id"] for s in stats}
        assert "Transport" in categories
        assert "Food" in categories

    def test_stats_unauthenticated(self, client: TestClient):
        res = client.get("/api/emissions/stats")
        assert res.status_code == 401
