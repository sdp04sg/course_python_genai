import base64

import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.main import create_app


@pytest.fixture(autouse=True)
def no_site_password(monkeypatch):
    # Keep tests independent of any APP_PASSWORD in the developer's .env.
    monkeypatch.delenv("APP_PASSWORD", raising=False)


def _basic_auth(password: str) -> dict[str, str]:
    token = base64.b64encode(f"me:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def test_site_password_protects_everything_except_health(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_PASSWORD", "correct horse")
    with TestClient(create_app(tmp_path / "progress.sqlite3")) as client:
        assert client.get("/api/health").status_code == 200

        locked = client.get("/api/courses")
        assert locked.status_code == 401
        assert locked.headers["WWW-Authenticate"].startswith("Basic")
        assert client.get("/docs").status_code == 401
        assert client.get("/api/courses", headers=_basic_auth("wrong")).status_code == 401
        assert client.get("/api/courses", headers={"Authorization": "Basic !!"}).status_code == 401

        assert client.get("/api/courses", headers=_basic_auth("correct horse")).status_code == 200


def test_serves_the_built_web_app_alongside_the_api(tmp_path):
    web_dist = tmp_path / "dist"
    web_dist.mkdir()
    (web_dist / "index.html").write_text("<h1>Build & Learn</h1>", encoding="utf-8")
    with TestClient(create_app(tmp_path / "progress.sqlite3", web_dist)) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert "Build & Learn" in page.text
        assert client.get("/api/health").json() == {"status": "ok"}
        assert client.put("/api/progress/nope", json={"completed": True}).status_code == 404


def test_courses_and_progress_are_available_and_persisted(tmp_path):
    app = create_app(tmp_path / "progress.sqlite3")
    with TestClient(app) as client:
        courses = client.get("/api/courses")
        assert courses.status_code == 200
        assert len(courses.json()) == 5

        updated = client.put("/api/progress/python-setup", json={"completed": True})
        assert updated.status_code == 200
        assert client.get("/api/progress").json() == {"python-setup": True}

    reopened_app = create_app(tmp_path / "progress.sqlite3")
    with TestClient(reopened_app) as reopened_client:
        assert reopened_client.get("/api/progress").json() == {"python-setup": True}


def test_progress_rejects_unknown_lessons(tmp_path):
    with TestClient(create_app(tmp_path / "progress.sqlite3")) as client:
        response = client.put("/api/progress/not-a-lesson", json={"completed": True})
    assert response.status_code == 404


def test_chat_explains_when_provider_is_not_configured(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with TestClient(create_app(tmp_path / "progress.sqlite3")) as client:
        response = client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Help me learn Python"}]},
        )
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_chat_uses_the_configured_openai_compatible_provider(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://provider.example/v1")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    class MockClient:
        def __init__(self, timeout):
            assert timeout == 30.0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

        async def post(self, url, headers, json):
            assert url == "https://provider.example/v1/chat/completions"
            assert headers["Authorization"] == "Bearer test-key"
            assert json["model"] == "test-model"
            assert json["messages"][0]["role"] == "system"
            return main.httpx.Response(
                200,
                json={"choices": [{"message": {"content": "Try a small example."}}]},
                request=main.httpx.Request("POST", url),
            )

    monkeypatch.setattr(main.httpx, "AsyncClient", MockClient)
    with TestClient(create_app(tmp_path / "progress.sqlite3")) as client:
        response = client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Help me learn Python"}]},
        )
    assert response.status_code == 200
    assert response.json() == {"reply": "Try a small example."}
