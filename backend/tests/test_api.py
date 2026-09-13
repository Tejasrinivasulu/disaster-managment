"""API tests for health, auth, disasters, prediction, and optimization."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402
from app.ml.predictor import predictor  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def auth_header(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "admin@disaster.local", "password": "admin123"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"


def test_login_invalid(client):
    r = client.post(
        "/api/auth/login",
        data={"username": "admin@disaster.local", "password": "wrong"},
    )
    assert r.status_code == 401


def test_list_disasters(client, auth_header):
    r = client.get("/api/disasters", headers=auth_header)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_create_resource(client, auth_header):
    depots = client.get("/api/resources/depots", headers=auth_header)
    assert depots.status_code == 200
    depot_id = depots.json()[0]["id"]
    r = client.post(
        "/api/resources",
        headers=auth_header,
        json={
            "depot_id": depot_id,
            "resource_type": "food_packets",
            "name": "Test Packets",
            "quantity_available": 100,
            "unit": "packets",
        },
    )
    assert r.status_code == 201
    assert r.json()["name"] == "Test Packets"


def test_predict_demand(client, auth_header):
    if not predictor.ready:
        pytest.skip("ML models not trained")
    r = client.post(
        "/api/predict/demand",
        headers=auth_header,
        json={
            "latitude": 13.6288,
            "longitude": 79.4192,
            "population": 50000,
            "population_density": 1200,
            "vulnerability_score": 0.72,
            "severity_score": 0.85,
            "building_damage_pct": 35,
            "road_damage_pct": 20,
            "rainfall": 150,
            "humidity": 80,
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["food_demand"] > 0
    assert body["water_demand_litres"] > 0
    assert "confidence" in body
    assert "base_demand" in body


def test_predict_invalid_input(client, auth_header):
    r = client.post(
        "/api/predict/demand",
        headers=auth_header,
        json={"latitude": 13.6},
    )
    assert r.status_code == 422


def test_optimization(client, auth_header):
    disasters = client.get("/api/disasters", headers=auth_header).json()
    disaster_id = disasters[0]["id"]
    r = client.post(
        "/api/optimization/allocate",
        headers=auth_header,
        json={"disaster_id": disaster_id},
    )
    assert r.status_code == 200, r.text
    assert "allocations" in r.json()


def test_mission_create(client, auth_header):
    disasters = client.get("/api/disasters", headers=auth_header).json()
    teams = client.get("/api/teams", headers=auth_header).json()
    d = disasters[0]
    zone_id = d["zones"][0]["id"]
    r = client.post(
        "/api/missions",
        headers=auth_header,
        json={
            "title": "Test Relief Mission",
            "instructions": "Deliver supplies",
            "disaster_id": d["id"],
            "zone_id": zone_id,
            "team_id": teams[0]["id"],
            "priority": "high",
            "resources_json": {"food_packets": 200},
        },
    )
    assert r.status_code == 201, r.text
