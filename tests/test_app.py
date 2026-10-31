
import pytest
import app as application


class FakeModel:

    def predict(self, reviews):
        return ["Positive"]

    def predict_proba(self, reviews):
        return [[0.85, 0.15]]


@pytest.fixture
def client(monkeypatch):

    monkeypatch.setattr(
        application,
        "sentiment_model",
        FakeModel()
    )

    monkeypatch.setattr(
        application,
        "fake_review_model",
        FakeModel()
    )

    application.app.config["TESTING"] = True

    with application.app.test_client() as client:
        yield client


def test_homepage(client):

    response = client.get("/")

    assert response.status_code == 200
    assert b"Product Review Analyzer" in response.data


def test_health_endpoint(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_empty_review(client):

    response = client.post(
        "/",
        data={"review": ""}
    )

    assert response.status_code == 200
    assert b"Please enter a product review" in response.data


def test_long_review(client):

    response = client.post(
        "/",
        data={"review": "A" * 5001}
    )

    assert response.status_code == 200
    assert b"5000 characters" in response.data


def test_review_submission(client):

    response = client.post(
        "/",
        data={"review": "Excellent product and great quality!"}
    )

    assert response.status_code == 200
    assert b"Positive" in response.data
