import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from serving.fast_api import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health_check")
    assert response.status_code == 200
    assert response.json() == "ok"


def test_predict():
    response = client.post("/predict", json={"text": ["this is test"]})
    assert response.status_code == 200
    probs = response.json()["probs"][0]
    assert len(probs) == 2
    assert sum(probs) == pytest.approx(1.0)
